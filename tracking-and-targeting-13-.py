import cv2, numpy as np, pygame, math, sys, logging
from collections import deque

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# -----------------------------
# GUI setup
# -----------------------------
WIDTH, HEIGHT = 800, 600
WHITE, RED, GREEN, BLUE, YELLOW = (255,255,255), (255,0,0), (0,255,0), (0,0,255), (255,215,0)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Tracking + Multi Lock + Cycle")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 22)
display_surface = pygame.Surface((WIDTH, HEIGHT))

# -----------------------------
# Camera
# -----------------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
if not cap.isOpened():
    print("Failed to open camera."); pygame.quit(); sys.exit(1)

# -----------------------------
# Haar Cascade
# -----------------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
def detect_faces(gray):
    faces = face_cascade.detectMultiScale(gray, 1.1, 5, minSize=(30,30))
    return [("face",(x,y,w,h)) for (x,y,w,h) in faces]

# -----------------------------
# Protected zones
# -----------------------------
PROTECTED_ZONES = [(50,40,160,120),(420,220,180,120)]
def apply_protection_mask(gray,zones):
    for (x,y,w,h) in zones:
        gray[y:y+h,x:x+w]=0
    return gray
def rect_scale_to_display(x,y,w,h,src_w=640,src_h=360,dst_w=WIDTH,dst_h=HEIGHT):
    return int(x*dst_w/src_w), int(y*dst_h/src_h), int(w*dst_w/src_w), int(h*dst_h/src_h)

# -----------------------------
# Kalman Track
# -----------------------------
class KalmanTrack:
    def __init__(self,tid,cx,cy):
        self.id=tid
        self.x=np.array([[cx],[cy],[0.0],[0.0]],dtype=np.float32)
        self.P=np.eye(4,dtype=np.float32)*50.0
        self.Q=np.eye(4,dtype=np.float32)*1.0
        self.R=np.eye(2,dtype=np.float32)*5.0
        self.H=np.array([[1,0,0,0],[0,1,0,0]],dtype=np.float32)
        self.history=deque(maxlen=32)
        self.label="face"; self.last_bbox=None; self.time_since_update=0
    def F(self,dt): return np.array([[1,0,dt,0],[0,1,0,dt],[0,0,1,0],[0,0,0,1]],dtype=np.float32)
    def predict(self,dt=1/30.0):
        Fm=self.F(dt); self.x=Fm@self.x; self.P=Fm@self.P@Fm.T+self.Q; self.time_since_update+=1
        return float(self.x[0,0]),float(self.x[1,0])
    def update(self,z,bbox=None):
        z=np.array(z,dtype=np.float32).reshape(2,1)
        y=z-(self.H@self.x); S=self.H@self.P@self.H.T+self.R
        try: K=self.P@self.H.T@np.linalg.inv(S)
        except: S=S+np.eye(2)*1e-3; K=self.P@self.H.T@np.linalg.inv(S)
        self.x=self.x+K@y; I=np.eye(4); self.P=(I-K@self.H)@self.P; self.time_since_update=0
        if bbox is not None: self.last_bbox=bbox
    def get_position(self): return float(self.x[0,0]),float(self.x[1,0])
    def get_velocity(self): return float(self.x[2,0]),float(self.x[3,0])

# -----------------------------
# Greedy Tracker
# -----------------------------
class GreedyMultiTracker:
    def __init__(self,max_age=10,dist_threshold=70.0,max_tracks=12):
        self.tracks=[]; self.next_id=0; self.max_age=max_age
        self.dist_threshold=dist_threshold; self.max_tracks=max_tracks; self.dt=1/30.0
    def step(self,detections):
        for t in self.tracks: t.predict(self.dt)
        det_centers=[(x+w/2,y+h/2) for _,(x,y,w,h) in detections]
        det_bboxes=[(x,y,w,h) for _,(x,y,w,h) in detections]
        used=set()
        for di,(cx,cy) in enumerate(det_centers):
            best=None; bestd=float('inf')
            for ti,t in enumerate(self.tracks):
                if ti in used: continue
                tx,ty=t.get_position(); d=math.hypot(tx-cx,ty-cy)
                if d<bestd: bestd=d; best=ti
            if best is not None and bestd<=self.dist_threshold:
                t=self.tracks[best]; t.update([cx,cy],bbox=det_bboxes[di])
                t.history.append((int(cx*WIDTH/640),int(cy*HEIGHT/360))); used.add(best)
            else:
                if len(self.tracks)<self.max_tracks:
                    t=KalmanTrack(self.next_id,cx,cy)
                    t.history.append((int(cx*WIDTH/640),int(cy*HEIGHT/360)))
                    self.tracks.append(t); self.next_id+=1
        self.tracks=[t for t in self.tracks if t.time_since_update<=self.max_age]
        return self.tracks

# -----------------------------
# Auto targeting + reticle
# -----------------------------
def target_score(track,center=(WIDTH//2,HEIGHT//2)):
    area=0
    if track.last_bbox is not None: x,y,w,h=track.last_bbox; area=w*h
    cx,cy=track.get_position(); cx_disp=int(cx*WIDTH/640); cy_disp=int(cy*HEIGHT/360)
    dist=math.hypot(cx_disp-center[0],cy_disp-center[1])
    return area*0.1 - dist*0.2 + len(track.history)*2 - track.time_since_update*3

def pick_target(tracks,protected,mouse_pos,locked_ids,current_lock_index):
    # If locked IDs exist, check attackers first
    if locked_ids:
        for tid in locked_ids:
            t = next((tr for tr in tracks if tr.id == tid), None)
            if t:
                vx, vy = t.get_velocity()
                cx, cy = t.get_position()
                cx_disp = int(cx * WIDTH / 640); cy_disp = int(cy * HEIGHT / 360)
                dx = (WIDTH//2) - cx_disp; dy = (HEIGHT//2) - cy_disp
                if vx*dx + vy*dy > 0:  # moving toward center
                    return t
        # Otherwise cycle
        tid = locked_ids[current_lock_index % len(locked_ids)]
        return next((tr for tr in tracks if tr.id == tid), None)
    # No locks: bias toward mouse
    mx,my=mouse_pos; best=None; bests=-1e9
    for t in tracks:
        cx,cy=t.get_position(); cx_disp=int(cx*WIDTH/640); cy_disp=int(cy*HEIGHT/360)
        if any(cx_disp>=x and cx_disp<=x+w and cy_disp>=y and cy_disp<=y+h for (x,y,w,h) in protected): continue
        dist_mouse=math.hypot(mx-cx_disp,my-cy_disp)
        s=target_score(t)-dist_mouse*0.3
        if s>bests: bests=s; best=t
    return best

class Reticle:
    def __init__(self): self.pos=np.array([WIDTH//2,HEIGHT//2],dtype=np.float32); self.alpha=0.2
    def update(self,t):
        if t is None: self.pos=(1-self.alpha)*self.pos+self.alpha*np.array([WIDTH//2,HEIGHT//2],dtype=np.float32); return
        cx,cy=t.get_position(); vx,vy=t.get_velocity()
        cx_disp=cx*WIDTH/640; cy_disp=cy*HEIGHT/360
        tx=cx_disp+vx*(WIDTH/640)*0.03; ty=cy_disp+vy*(HEIGHT/360)*0.03
        self.pos=(1-self.alpha)*self.pos+self.alpha*np.array([tx,ty],dtype=np.float32)
    def draw(self,surf):
        x,y=int(self.pos[0]),int(self.pos[1])
        pygame.draw.line(surf,YELLOW,(x-12,y),(x+12,y),2)
        pygame.draw.line(surf,YELLOW,(x,y-12),(x,y+12),2)
        pygame.draw.circle(surf,YELLOW,(x,y),16,1)

# -----------------------------
# Main loop
# -----------------------------
tracker=GreedyMultiTracker(); reticle=Reticle()
locked_ids=[]; current_lock_index=0
click_indicator_pos=None; click_indicator_timer=0
LOCK_THRESHOLD=30; mouse_pos=(WIDTH//2,HEIGHT//2)

try:
    while True:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type==pygame.QUIT: raise KeyboardInterrupt
            elif event.type==pygame.MOUSEMOTION:
                mouse_pos=event.pos
            elif event.type==pygame.MOUSEBUTTONDOWN:
                mx,my=pygame.mouse.get_pos()
                if event.button==1:  # left click to add lock
                    click_indicator_pos=(mx,my); click_indicator_timer=15
                    closest_id,min_dist=None,float('inf')
                    for t in tracker.tracks:
                        cx,cy=t.get_position()
                        cx_disp=int(cx*WIDTH/640); cy_disp=int(cy*HEIGHT/360)
                        dist=math.hypot(mx-cx_disp,my-cy_disp)
                        if dist<min_dist: min_dist=dist; closest_id=t.id
                    if closest_id is not None and min_dist<=LOCK_THRESHOLD:
                        if closest_id not in locked_ids:
                            locked_ids.append(closest_id)
                        logging.info(f"Locked target ID {closest_id}")
                elif event.button==3:  # right click clears all locks
                    locked_ids.clear(); click_indicator_pos=None; click_indicator_timer=0
                    logging.info("Cleared all locks")
            elif event.type==pygame.KEYDOWN:
                if event.key==pygame.K_TAB and locked_ids:
                    current_lock_index=(current_lock_index+1)%len(locked_ids)
                    logging.info(f"Cycled to locked target ID {locked_ids[current_lock_index]}")

        # --- Frame capture ---
        ret,frame=cap.read()
        if not ret or frame is None or frame.size==0:
            clock.tick(30); continue

        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        gray_masked=apply_protection_mask(gray.copy(),PROTECTED_ZONES)
        detections=detect_faces(gray_masked)

        # --- Tracking ---
        tracks=tracker.step(detections)
        protected_display=[rect_scale_to_display(x,y,w,h,640,360,WIDTH,HEIGHT) for (x,y,w,h) in PROTECTED_ZONES]

        # --- Target selection ---
        target_track=pick_target(tracks,protected_display,mouse_pos,locked_ids,current_lock_index)
        reticle.update(target_track)

        # --- Drawing ---
        vis=cv2.resize(frame,(WIDTH,HEIGHT))
        overlay=vis.copy()
        for (x,y,w,h) in protected_display:
            cv2.rectangle(overlay,(x,y),(x+w,y+h),(0,0,0),-1)
        vis=cv2.addWeighted(overlay,0.25,vis,0.75,0)
        rgb=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
        arr=np.transpose(rgb,(1,0,2)).copy()
        pygame.surfarray.blit_array(display_surface,arr)
        screen.blit(display_surface,(0,0))

        # Draw tracks
        for t in tracks:
            cx,cy=t.get_position()
            cx_disp=int(cx*WIDTH/640); cy_disp=int(cy*HEIGHT/360)
            pygame.draw.circle(screen,RED,(cx_disp,cy_disp),6)
            screen.blit(font.render(f"ID {t.id}",True,BLUE),(cx_disp+8,cy_disp-18))
            for i in range(1,len(t.history)):
                pygame.draw.line(screen,RED,t.history[i-1],t.history[i],2)

        # Highlight locked targets
        for idx,tid in enumerate(locked_ids):
            t=next((tr for tr in tracks if tr.id==tid),None)
            if t:
                cx,cy=t.get_position()
                cx_disp=int(cx*WIDTH/640); cy_disp=int(cy*HEIGHT/360)
                color=GREEN if idx!=current_lock_index else YELLOW
                pygame.draw.circle(screen,color,(cx_disp,cy_disp),12,2)
                screen.blit(font.render(f"LOCKED {tid}",True,color),(cx_disp+12,cy_disp-24))

        # Draw reticle
        reticle.draw(screen)

        # Draw click indicator circle if active
        if click_indicator_timer>0 and click_indicator_pos is not None:
            pygame.draw.circle(screen,YELLOW,click_indicator_pos,LOCK_THRESHOLD,2)
            click_indicator_timer-=1

        # HUD
        fps=clock.get_fps()
        status=f"FPS: {fps:.1f} | Tracks: {len(tracks)} | Dets: {len(detections)} | Locks: {locked_ids if locked_ids else 'Auto'}"
        screen.blit(font.render(status,True,GREEN),(10,10))

        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    logging.info("Stopped by user")
finally:
    cap.release(); pygame.quit(); sys.exit()



