import cv2, numpy as np, pygame, math, sys, logging, time
from collections import deque
from scipy.optimize import linear_sum_assignment

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# -----------------------------
# GUI setup
# -----------------------------
WIDTH, HEIGHT = 960, 540
WHITE, RED, GREEN, BLUE, YELLOW, ORANGE, CYAN, MAGENTA = (
    (255,255,255), (255,0,0), (0,255,0), (0,0,255),
    (255,215,0), (255,140,0), (0,255,255), (255,0,255)
)

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Tracking — Auto X‑Ray + Anomaly Detection")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 22)
display_surface = pygame.Surface((WIDTH, HEIGHT))

# -----------------------------
# Camera
# -----------------------------
CAP_W, CAP_H = 640, 360
def open_camera():
    cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_W)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_H)
    cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
    return cap

cap = open_camera()
if not cap.isOpened():
    print("Failed to open camera."); pygame.quit(); sys.exit(1)

# -----------------------------
# Detectors
# -----------------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
backSub = cv2.createBackgroundSubtractorMOG2(history=600, varThreshold=26, detectShadows=True)

# -----------------------------
# Tunables
# -----------------------------
sensitivity = 0.6
stability   = 0.6
FACE_EVERY_N = 4
MAX_TRACKS = 48

# Anomaly thresholds
VEL_Z_THRESH = 2.2
HEADING_DELTA_THRESH = math.radians(75)
AREA_JUMP_RATIO = 1.8
LINGER_FRAMES = 90
LINGER_RADIUS = 35
GLOBAL_MOTION_Z = 2.5

def motion_params_from_sensitivity(s):
    varThresh = int(np.interp(s, [0,1], [52, 14]))
    min_area = int(np.interp(s, [0,1], [1400, 240]))
    return varThresh, min_area

def tracking_params_from_stability(stab):
    confirm_N = int(np.interp(stab, [0,1], [1, 4]))
    max_age   = int(np.interp(stab, [0,1], [10, 6]))
    gate_mahal = np.interp(stab, [0,1], [7.5, 4.2])
    Q_scale = np.interp(stab, [0,1], [1.5, 0.7])
    R_scale = np.interp(stab, [0,1], [1.3, 0.85])
    return confirm_N, max_age, gate_mahal, Q_scale, R_scale

def detect_faces(gray):
    faces = face_cascade.detectMultiScale(gray, 1.08, 4, minSize=(24,24))
    return [("face",(x,y,w,h)) for (x,y,w,h) in faces]

# Always return detections + mask
def detect_motion(frame, sensitivity, kernel_size=3):
    varThresh, min_area = motion_params_from_sensitivity(sensitivity)
    backSub.setVarThreshold(varThresh)
    fgMask = backSub.apply(frame)
    _, fgMaskBin = cv2.threshold(fgMask, 200, 255, cv2.THRESH_BINARY)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    fgMaskClean = cv2.morphologyEx(fgMaskBin, cv2.MORPH_OPEN, kernel, iterations=1)
    fgMaskClean = cv2.morphologyEx(fgMaskClean, cv2.MORPH_CLOSE, kernel, iterations=1)
    contours, _ = cv2.findContours(fgMaskClean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    border = 6
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area: continue
        x,y,w,h = cv2.boundingRect(cnt)
        if x < border or y < border or (x+w) > (CAP_W-border) or (y+h) > (CAP_H-border): continue
        detections.append(("motion",(x,y,w,h)))
    return detections, fgMaskClean

# -----------------------------
# Kalman Track with anomaly detection
# -----------------------------
class KalmanTrack:
    def __init__(self, tid, cx, cy, Q_scale=1.0, R_scale=1.0, label=None, bbox=None):
        self.id = tid
        self.x = np.array([[cx],[cy],[0.0],[0.0]], dtype=np.float32)
        self.P = np.eye(4, dtype=np.float32) * 50.0
        self.Q_base = np.diag([1.0,1.0,3.0,3.0]).astype(np.float32)*Q_scale
        self.R_base = np.diag([4.0,4.0]).astype(np.float32)*R_scale
        self.H = np.array([[1,0,0,0],[0,1,0,0]], dtype=np.float32)
        self.history=deque(maxlen=64)
        self.label=label; self.last_bbox=bbox
        self.time_since_update=0; self.hits=0; self.confirmed=False
        # anomaly state
        self.vel_history=deque(maxlen=120)
        self.heading_prev=None; self.area_prev=None
        self.linger_origin=None; self.linger_start_frame=None
        self.is_anomaly=False; self.anomaly_reason=""

    def F(self,dt): return np.array([[1,0,dt,0],[0,1,0,dt],[0,0,1,0],[0,0,0,1]],dtype=np.float32)
    def predict(self,dt=1/30.0):
        Fm=self.F(dt); self.x=Fm@self.x; self.P=Fm@self.P@Fm.T+self.Q_base
        self.time_since_update+=1; return float(self.x[0,0]),float(self.x[1,0])
    def update(self,z,bbox=None,label=None,frame_idx=None):
        z=np.array(z,dtype=np.float32).reshape(2,1)
        y=z-(self.H@self.x); S=self.H@self.P@self.H.T+self.R_base
        K=self.P@self.H.T@np.linalg.inv(S+np.eye(2)*1e-6)
        self.x=self.x+K@y; I=np.eye(4,dtype=np.float32); self.P=(I-K@self.H)@self.P
        self.time_since_update=0; self.hits+=1
        if bbox is not None: self.last_bbox=bbox
        if label is not None: self.label=label
        # anomaly checks
        vx,vy=self.get_velocity(); vmag=math.hypot(vx,vy)
        self.vel_history.append(vmag)
        heading=math.atan2(vy,vx) if vmag>1e-3 else self.heading_prev
        heading_delta=0.0
        if self.heading_prev is not None and heading is not None:
            diff=heading-self.heading_prev
            while diff>math.pi: diff-=2*math.pi
            while diff<-math.pi: diff+=2*math.pi
            heading_delta=abs(diff)
        self.heading_prev=heading
        area_jump=1.0
        if self.last_bbox is not None:
            x,y,w,h=self.last_bbox; area=w*h
            if self.area_prev: area_jump=(area/self.area_prev) if self.area_prev>0 else 1.0
            self.area_prev=area
        cx,cy=self.get_position()
        cx_disp=int(cx*WIDTH/CAP_W); cy_disp=int(cy*HEIGHT/CAP_H)
        if self.linger_origin is None:
            self.linger_origin=(cx_disp,cy_disp); self.linger_start_frame=frame_idx
        else:
            dist=math.hypot(cx_disp-self.linger_origin[0],cy_disp-self.linger_origin[1])
            if dist>LINGER_RADIUS:
                self.linger_origin=(cx_disp,cy_disp); self.linger_start_frame=frame_idx
        linger_frames=(frame_idx-self.linger_start_frame) if (self.linger_start_frame is not None and frame_idx is not None) else 0
        self.is_anomaly=False; self.anomaly_reason=""
        if len(self.vel_history)>=30:
            vmean=float(np.mean(self.vel_history)); vstd=float(np.std(self.vel_history))+1e-6
            z=(vmag-vmean)/vstd
            if z>=VEL_Z_THRESH:
                self.is_anomaly=True; self.anomaly_reason="velocity spike"
        if heading_delta>=HEADING_DELTA_THRESH:
            self.is_anomaly=True; self.anomaly_reason="direction change"
        if area_jump>=AREA_JUMP_RATIO:
            self.is_anomaly=True; self.anomaly_reason="size jump"
        if linger_frames>=LINGER_FRAMES:
            self.is_anomaly=True; self.anomaly_reason="lingering"

    def get_position(self): return float(self.x[0,0]),float(self.x[1,0])
    def get_velocity(self): return float(self.x[2,0]),float(self.x[3,0])

# -----------------------------
# MultiTrackerHungarian
# -----------------------------
class MultiTrackerHungarian:
    def __init__(self,max_age=8,confirm_N=3,gate_mahal=6.0,Q_scale=1.0,R_scale=1.0,max_tracks=48):
        self.tracks=[]; self.next_id=0
        self.max_age=max_age; self.confirm_N=confirm_N; self.gate_mahal=gate_mahal
        self.Q_scale=Q_scale; self.R_scale=R_scale; self.max_tracks=max_tracks; self.dt=1/30.0
        self.frame_idx=0

    def step(self,detections):
        self.frame_idx+=1
        for t in self.tracks: t.predict(self.dt)
        det_centers=[((x+w/2),(y+h/2)) for _,(x,y,w,h) in detections]
        det_bboxes=[b for _,b in detections]; det_labels=[label for label,_ in detections]
        T,D=len(self.tracks),len(det_centers)
        if T>0 and D>0:
            cost=np.zeros((T,D),dtype=np.float32)
            for i,tr in enumerate(self.tracks):
                S=tr.H@tr.P@tr.H.T+tr.R_base; invS=np.linalg.inv(S+np.eye(2)*1e-6); hx=tr.H@tr.x
                for j,dc in enumerate(det_centers):
                    diff=np.array(dc,dtype=np.float32).reshape(2,1)-hx
                    cost[i,j]=float(diff.T@invS@diff)
            row_ind,col_ind=linear_sum_assignment(cost)
            matched_tracks=set(); matched_dets=set()
            for r,c in zip(row_ind,col_ind):
                if cost[r,c]<=self.gate_mahal:
                    tr=self.tracks[r]
                    tr.update(det_centers[c],bbox=det_bboxes[c],label=det_labels[c],frame_idx=self.frame_idx)
                    tr.history.append((int(tr.x[0,0]*WIDTH/CAP_W),int(tr.x[1,0]*HEIGHT/CAP_H)))
                    matched_tracks.add(r); matched_dets.add(c)
            for j in range(D):
                if j not in matched_dets and len(self.tracks)<self.max_tracks:
                    cx,cy=det_centers[j]
                    t=KalmanTrack(self.next_id,cx,cy,Q_scale=self.Q_scale,R_scale=self.R_scale,
                                  label=det_labels[j],bbox=det_bboxes[j])
                    t.history.append((int(cx*WIDTH/CAP_W),int(cy*HEIGHT/CAP_H)))
                    self.tracks.append(t); self.next_id+=1
            survivors=[]
            for i,tr in enumerate(self.tracks):
                if i not in matched_tracks: tr.time_since_update+=1
                tr.confirmed=(tr.hits>=self.confirm_N)
                if tr.time_since_update<=self.max_age: survivors.append(tr)
            self.tracks=survivors
        else:
            for j in range(D):
                if len(self.tracks)<self.max_tracks:
                    cx,cy=det_centers[j]
                    t=KalmanTrack(self.next_id,cx,cy,Q_scale=self.Q_scale,R_scale=self.R_scale,
                                  label=det_labels[j],bbox=det_bboxes[j])
                    t.history.append((int(cx*WIDTH/CAP_W),int(cy*HEIGHT/CAP_H)))
                    self.tracks.append(t); self.next_id+=1
            if D==0:
                self.tracks=[t for t in self.tracks if t.time_since_update<=self.max_age]
        return self.tracks

# -----------------------------
# Target scoring & selection
# -----------------------------
def target_score(track, center=(WIDTH//2, HEIGHT//2)):
    face_bonus = 20.0 if (track.label == "face") else 0.0
    confirmed_bonus = 10.0 if track.confirmed else 0.0
    area = 0.0
    if track.last_bbox is not None:
        x,y,w,h = track.last_bbox; area = w*h
    cx, cy = track.get_position()
    cx_disp = int(cx * WIDTH / CAP_W); cy_disp = int(cy * HEIGHT / CAP_H)
    dist_center = math.hypot(cx_disp - center[0], cy_disp - center[1])
    recent_penalty = track.time_since_update * 6.0
    age_bonus = min(track.hits*2.0, 30.0)
    vx, vy = track.get_velocity(); motion_mag = math.hypot(vx, vy)
    return (area*0.05) + face_bonus + confirmed_bonus + age_bonus + (motion_mag*8.0) - (dist_center*0.25) - recent_penalty

def pick_target(tracks, mouse_pos, locked_ids, current_lock_index):
    if locked_ids:
        for tid in locked_ids:
            t = next((tr for tr in tracks if tr.id == tid), None)
            if t:
                vx, vy = t.get_velocity(); cx, cy = t.get_position()
                cx_disp = int(cx * WIDTH / CAP_W); cy_disp = int(cy * HEIGHT / CAP_H)
                dx = (WIDTH//2) - cx_disp; dy = (HEIGHT//2) - cy_disp
                if vx*dx + vy*dy > 0: return t
        tid = locked_ids[current_lock_index % len(locked_ids)]
        return next((tr for tr in tracks if tr.id == tid), None)
    mx,my = mouse_pos; best=None; bests=-1e9
    for t in tracks:
        cx,cy = t.get_position()
        cx_disp=int(cx*WIDTH/CAP_W); cy_disp=int(cy*HEIGHT/CAP_H)
        dist_mouse=math.hypot(mx-cx_disp,my-cy_disp)
        s=target_score(t)-dist_mouse*0.25
        if s>bests: bests=s; best=t
    return best

# -----------------------------
# Reticle and sliders
# -----------------------------
class Reticle:
    def __init__(self):
        self.pos = np.array([WIDTH//2, HEIGHT//2], dtype=np.float32)
        self.alpha = 0.22; self.snap_gain = 0.06
    def update(self,t):
        center = np.array([WIDTH//2, HEIGHT//2], dtype=np.float32)
        if t is None:
            self.pos=(1-self.alpha)*self.pos+self.alpha*center; return
        cx,cy=t.get_position(); vx,vy=t.get_velocity()
        cx_disp=cx*WIDTH/CAP_W; cy_disp=cy*HEIGHT/CAP_H
        tx=cx_disp+vx*(WIDTH/CAP_W)*0.035; ty=cy_disp+vy*(HEIGHT/CAP_H)*0.035
        target=np.array([tx,ty],dtype=np.float32)
        self.pos=self.pos+self.snap_gain*(target-self.pos)
        self.pos=(1-self.alpha)*self.pos+self.alpha*target
    def draw(self,surf):
        x,y=int(self.pos[0]),int(self.pos[1])
        pygame.draw.line(surf,YELLOW,(x-12,y),(x+12,y),2)
        pygame.draw.line(surf,YELLOW,(x,y-12),(x,y+12),2)
        pygame.draw.circle(surf,YELLOW,(x,y),16,1)

class Slider:
    def __init__(self,x,y,w,label,init=0.5):
        self.rect=pygame.Rect(x,y,w,10); self.handle_x=x+int(init*w)
        self.label=label; self.value=init; self.dragging=False
    def handle_event(self,event):
        if event.type==pygame.MOUSEBUTTONDOWN and event.button==1:
            if self.rect.collidepoint(event.pos) or abs(event.pos[0]-self.handle_x)<10: self.dragging=True
        elif event.type==pygame.MOUSEBUTTONUP and event.button==1: self.dragging=False
        elif event.type==pygame.MOUSEMOTION and self.dragging:
            x=np.clip(event.pos[0],self.rect.x,self.rect.x+self.rect.width)
            self.handle_x=int(x); self.value=(self.handle_x-self.rect.x)/self.rect.width
    def draw(self,surf):
        pygame.draw.rect(surf,WHITE,self.rect,1)
        pygame.draw.rect(surf,BLUE,(self.rect.x,self.rect.y+4,self.handle_x-self.rect.x,2))
        pygame.draw.circle(surf,CYAN,(self.handle_x,self.rect.y+5),6)
        text=font.render(f"{self.label}: {self.value:.2f}",True,WHITE)
        surf.blit(text,(self.rect.x,self.rect.y-18))

# -----------------------------
# Main loop
# -----------------------------
confirm_N,max_age,gate_mahal,Q_scale,R_scale=tracking_params_from_stability(stability)
tracker=MultiTrackerHungarian(max_age=max_age,confirm_N=confirm_N,gate_mahal=gate_mahal,
                              Q_scale=Q_scale,R_scale=R_scale,max_tracks=MAX_TRACKS)
reticle=Reticle()
locked_ids=[]; current_lock_index=0
click_indicator_pos=None; click_indicator_timer=0
LOCK_THRESHOLD=30; mouse_pos=(WIDTH//2,HEIGHT//2)
slider_sens=Slider(10,HEIGHT-40,240,"Sensitivity",init=sensitivity)
slider_stab=Slider(270,HEIGHT-40,240,"Stability",init=stability)
frame_count=0; last_reopen_time=0
frames_no_dets=0; camera_hiccup=False
global_motion_hist=deque(maxlen=180)

try:
    while True:
        for event in pygame.event.get():
            if event.type==pygame.QUIT: raise KeyboardInterrupt
            elif event.type==pygame.MOUSEMOTION: mouse_pos=event.pos
            slider_sens.handle_event(event); slider_stab.handle_event(event)

        sensitivity=slider_sens.value; stability=slider_stab.value
        confirm_N,max_age,gate_mahal,Q_scale,R_scale=tracking_params_from_stability(stability)
        tracker.confirm_N=confirm_N; tracker.max_age=max_age
        tracker.gate_mahal=gate_mahal; tracker.Q_scale=Q_scale; tracker.R_scale=R_scale

        ret,frame=cap.read()
        if not ret or frame is None or frame.size==0:
            camera_hiccup=True
            print("⚠️ Camera feed failed — another app may have grabbed the webcam.")
            logging.warning("Camera feed failed — possible conflict with another application.")
            if time.time()-last_reopen_time>1.0:
                cap.release(); time.sleep(0.2); cap=open_camera(); last_reopen_time=time.time()
            clock.tick(30); continue
        else: camera_hiccup=False

        gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
        detections_motion,motion_mask=detect_motion(frame,sensitivity)
        detections_faces=detect_faces(gray) if (frame_count%FACE_EVERY_N==0) else []
        frame_count+=1
        detections=detections_faces+detections_motion

        tracks=tracker.step(detections)
        target_track=pick_target(tracks,mouse_pos,locked_ids,current_lock_index)
        reticle.update(target_track)

        motion_heat=float(np.count_nonzero(motion_mask))/float(motion_mask.size)
        global_motion_hist.append(motion_heat)
        global_anomaly=False
        if len(global_motion_hist)>=60:
            g_mean=float(np.mean(global_motion_hist)); g_std=float(np.std(global_motion_hist))+1e-6
            g_z=(motion_heat-g_mean)/g_std
            global_anomaly=abs(g_z)>=GLOBAL_MOTION_Z

        fps=clock.get_fps()
        frames_no_dets=frames_no_dets+1 if len(detections)==0 else 0
        auto_xray=(camera_hiccup or fps<18 or frames_no_dets>=60 or global_anomaly)

        if auto_xray:
            edges=cv2.Canny(gray,100,200)
            edges_rgb=cv2.cvtColor(edges,cv2.COLOR_GRAY2RGB)
            edges_resized=cv2.resize(edges_rgb,(WIDTH,HEIGHT))
            motion_color=cv2.applyColorMap(cv2.resize(motion_mask,(WIDTH,HEIGHT)),cv2.COLORMAP_HOT)
            xray=cv2.addWeighted(edges_resized,0.6,motion_color,0.6,0.0)
            arr=np.transpose(xray,(1,0,2)).copy()
            pygame.surfarray.blit_array(display_surface,arr)
            screen.blit(display_surface,(0,0))
            screen.blit(font.render("X‑RAY MODE (Auto)",True,CYAN),(WIDTH-180,10))
        else:
            vis=cv2.resize(frame,(WIDTH,HEIGHT))
            rgb=cv2.cvtColor(vis,cv2.COLOR_BGR2RGB)
            arr=np.transpose(rgb,(1,0,2)).copy()
            pygame.surfarray.blit_array(display_surface,arr)
            screen.blit(display_surface,(0,0))

        for t in tracks:
            cx,cy=t.get_position()
            cx_disp=int(cx*WIDTH/CAP_W); cy_disp=int(cy*HEIGHT/CAP_H)
            color=BLUE if (t.label=="face") else ORANGE
            pygame.draw.circle(screen,color,(cx_disp,cy_disp),6)
            lbl=f"{(t.label or 'ID').upper()} {t.id}{' ✓' if t.confirmed else ''}"
            if t.is_anomaly:
                pygame.draw.circle(screen,MAGENTA,(cx_disp,cy_disp),16,2)
                lbl+=f" ! {t.anomaly_reason}"
            screen.blit(font.render(lbl,True,WHITE),(cx_disp+8,cy_disp-18))
            for i in range(1,len(t.history)):
                pygame.draw.line(screen,color,t.history[i-1],t.history[i],2)

        reticle.draw(screen)
        fps=clock.get_fps()
        status=f"FPS: {fps:.1f} | Tracks: {len(tracks)} | Dets: {len(detections)}"
        screen.blit(font.render(status,True,WHITE),(10,10))
        if camera_hiccup:
            screen.blit(font.render("CAMERA LOST — Reopening...",True,RED),(10,32))
        if global_anomaly:
            screen.blit(font.render("GLOBAL ANOMALY DETECTED",True,MAGENTA),(10,54))

        slider_sens.draw(screen); slider_stab.draw(screen)
        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    logging.info("Stopped by user")
finally:
    try: cap.release()
    except: pass
    pygame.quit(); sys.exit()

