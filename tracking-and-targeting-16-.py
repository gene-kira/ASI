import cv2, numpy as np, pygame, math, sys, logging
from collections import deque
from scipy.optimize import linear_sum_assignment  # Hungarian

# -----------------------------
# Logging
# -----------------------------
logging.basicConfig(filename='app.log', level=logging.INFO,
                    format='%(asctime)s %(levelname)s: %(message)s')

# -----------------------------
# GUI setup
# -----------------------------
WIDTH, HEIGHT = 960, 540
WHITE, RED, GREEN, BLUE, YELLOW, ORANGE, CYAN = (255,255,255), (255,0,0), (0,255,0), (0,0,255), (255,215,0), (255,140,0), (0,255,255)

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Autonomous Tracking — Face + Motion, Sensitivity & Stability Controls")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 22)
display_surface = pygame.Surface((WIDTH, HEIGHT))

# -----------------------------
# Camera
# -----------------------------
CAP_W, CAP_H = 640, 360
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, CAP_W)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, CAP_H)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
if not cap.isOpened():
    print("Failed to open camera."); pygame.quit(); sys.exit(1)

# -----------------------------
# Detectors
# -----------------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")
backSub = cv2.createBackgroundSubtractorMOG2(history=800, varThreshold=24, detectShadows=True)

# Tunables (linked to sliders)
sensitivity = 0.6   # 0..1; higher = more sensitive motion (lower varThreshold & min area)
stability   = 0.6   # 0..1; higher = more stable tracking (higher confirmation, lower Q, tighter gating)
face_scale_factor = 1.08
face_min_neighbors = 4

def motion_params_from_sensitivity(s):
    # Lower varThreshold and min_area when sensitivity increases
    varThresh = int(np.interp(s, [0,1], [48, 14]))
    min_area = int(np.interp(s, [0,1], [1200, 220]))  # depends on resolution
    return varThresh, min_area

def tracking_params_from_stability(stab):
    # Confirmation frames and gating
    confirm_N = int(np.interp(stab, [0,1], [1, 4]))
    max_age   = int(np.interp(stab, [0,1], [10, 6]))
    gate_mahal = np.interp(stab, [0,1], [7.0, 4.0])  # Mahalanobis gate threshold
    # Kalman noises
    Q_scale = np.interp(stab, [0,1], [1.5, 0.6])
    R_scale = np.interp(stab, [0,1], [1.2, 0.8])
    return confirm_N, max_age, gate_mahal, Q_scale, R_scale

def detect_faces(gray):
    faces = face_cascade.detectMultiScale(
        gray, face_scale_factor, face_min_neighbors, minSize=(24,24))
    return [("face",(x,y,w,h)) for (x,y,w,h) in faces]

def detect_motion(frame, sensitivity, kernel_size=3):
    varThresh, min_area = motion_params_from_sensitivity(sensitivity)
    # Reconfigure varThreshold dynamically
    backSub.setVarThreshold(varThresh)

    fgMask = backSub.apply(frame)
    # Remove shadows (value ~127) by thresholding to 0/255
    _, fgMaskBin = cv2.threshold(fgMask, 200, 255, cv2.THRESH_BINARY)
    # Morphological cleanup
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (kernel_size, kernel_size))
    fgMaskClean = cv2.morphologyEx(fgMaskBin, cv2.MORPH_OPEN, kernel, iterations=1)
    fgMaskClean = cv2.morphologyEx(fgMaskClean, cv2.MORPH_CLOSE, kernel, iterations=1)

    contours, _ = cv2.findContours(fgMaskClean, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    detections = []
    border = 6  # ignore near borders (common false motion)
    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < min_area:
            continue
        x,y,w,h = cv2.boundingRect(cnt)
        if x < border or y < border or (x+w) > (CAP_W-border) or (y+h) > (CAP_H-border):
            continue
        detections.append(("motion",(x,y,w,h)))
    return detections

# -----------------------------
# Kalman Track
# -----------------------------
class KalmanTrack:
    def __init__(self, tid, cx, cy, Q_scale=1.0, R_scale=1.0, label=None, bbox=None):
        self.id     = tid
        self.x      = np.array([[cx],[cy],[0.0],[0.0]], dtype=np.float32)  # [x,y,vx,vy]
        self.P      = np.eye(4, dtype=np.float32) * 50.0
        self.Q_base = np.diag([1.0, 1.0, 3.0, 3.0]).astype(np.float32) * Q_scale
        self.R_base = np.diag([4.0, 4.0]).astype(np.float32) * R_scale
        self.H      = np.array([[1,0,0,0],[0,1,0,0]], dtype=np.float32)
        self.history= deque(maxlen=64)
        self.label  = label
        self.last_bbox = bbox
        self.time_since_update = 0
        self.age = 0
        self.hits = 0
        self.confirmed = False
        self.residuals = deque(maxlen=20)  # for adaptive tuning

    def F(self, dt):
        return np.array([
            [1,0,dt,0],
            [0,1,0,dt],
            [0,0,1, 0],
            [0,0,0, 1]
        ], dtype=np.float32)

    def predict(self, dt=1/30.0):
        Fm = self.F(dt)
        self.x = Fm @ self.x
        self.P = Fm @ self.P @ Fm.T + self.Q_base
        self.time_since_update += 1
        self.age += 1
        return float(self.x[0,0]), float(self.x[1,0])

    def update(self, z, bbox=None, label=None):
        z = np.array(z, dtype=np.float32).reshape(2,1)
        y = z - (self.H @ self.x)  # residual
        S = self.H @ self.P @ self.H.T + self.R_base
        try:
            K = self.P @ self.H.T @ np.linalg.inv(S)
        except:
            S = S + np.eye(2)*1e-3
            K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        I = np.eye(4, dtype=np.float32)
        self.P = (I - K @ self.H) @ self.P

        # Adaptive tuning: track residual magnitude
        res_mag = float(np.linalg.norm(y))
        self.residuals.append(res_mag)

        self.time_since_update = 0
        self.hits += 1
        if bbox is not None:
            self.last_bbox = bbox
        if label is not None:
            self.label = label

    def adapt_noise(self):
        # Increase R if residuals are high; decrease if low
        if len(self.residuals) >= 5:
            rmean = np.mean(self.residuals)
            # clamp scaling
            scale = np.clip(np.interp(rmean, [0.5, 10.0], [0.8, 1.6]), 0.6, 2.0)
            self.R_base = np.diag([4.0*scale, 4.0*scale]).astype(np.float32)

    def get_position(self):
        return float(self.x[0,0]), float(self.x[1,0])

    def get_velocity(self):
        return float(self.x[2,0]), float(self.x[3,0])

# -----------------------------
# Utilities
# -----------------------------
def bbox_center(b):
    x,y,w,h = b
    return (x + w/2.0, y + h/2.0)

def iou(b1, b2):
    x1,y1,w1,h1 = b1
    x2,y2,w2,h2 = b2
    xa = max(x1, x2)
    ya = max(y1, y2)
    xb = min(x1+w1, x2+w2)
    yb = min(y1+h1, y2+h2)
    inter = max(0, xb-xa) * max(0, yb-ya)
    union = w1*h1 + w2*h2 - inter
    return inter/union if union>0 else 0.0

def mahalanobis_cost(track, det_center):
    # cost based on position difference, approximated by covariance P
    z = np.array(det_center, dtype=np.float32).reshape(2,1)
    hx = track.H @ track.x
    diff = z - hx
    S = track.H @ track.P @ track.H.T + track.R_base
    try:
        invS = np.linalg.inv(S)
    except:
        invS = np.linalg.inv(S + np.eye(2)*1e-3)
    m = float(diff.T @ invS @ diff)  # scalar
    return m

# -----------------------------
# Multi-object tracker (Hungarian)
# -----------------------------
class MultiTrackerHungarian:
    def __init__(self, max_age=8, confirm_N=3, gate_mahal=6.0, Q_scale=1.0, R_scale=1.0, max_tracks=64):
        self.tracks = []
        self.next_id = 0
        self.max_age = max_age
        self.confirm_N = confirm_N
        self.gate_mahal = gate_mahal
        self.Q_scale = Q_scale
        self.R_scale = R_scale
        self.max_tracks = max_tracks
        self.dt = 1/30.0

    def step(self, detections):
        # Predict
        for t in self.tracks:
            t.predict(self.dt)
            t.adapt_noise()

        det_centers = [bbox_center(b) for _, b in detections]
        det_bboxes  = [b for _, b in detections]
        det_labels  = [label for label, _ in detections]

        T = len(self.tracks)
        D = len(det_centers)

        if T > 0 and D > 0:
            # Build cost matrix with Mahalanobis + IoU penalty
            cost = np.zeros((T, D), dtype=np.float32)
            for i, tr in enumerate(self.tracks):
                for j, dc in enumerate(det_centers):
                    m = mahalanobis_cost(tr, dc)
                    # Add an IoU preference: lower cost for higher IoU with last bbox
                    iou_bonus = 0.0
                    if tr.last_bbox is not None:
                        iou_bonus = (1.0 - iou(tr.last_bbox, det_bboxes[j])) * 0.5
                    cost[i, j] = m + iou_bonus

            row_ind, col_ind = linear_sum_assignment(cost)

            matched_tracks = set()
            matched_dets = set()

            # Apply gating
            for r, c in zip(row_ind, col_ind):
                tr = self.tracks[r]
                mcost = cost[r, c]
                if mcost <= self.gate_mahal:
                    tr.update(det_centers[c], bbox=det_bboxes[c], label=det_labels[c])
                    tr.history.append((int(tr.x[0,0]*WIDTH/CAP_W), int(tr.x[1,0]*HEIGHT/CAP_H)))
                    matched_tracks.add(r)
                    matched_dets.add(c)

            # Unmatched detections -> new tracks
            for j in range(D):
                if j not in matched_dets and len(self.tracks) < self.max_tracks:
                    cx, cy = det_centers[j]
                    t = KalmanTrack(self.next_id, cx, cy, Q_scale=self.Q_scale, R_scale=self.R_scale,
                                    label=det_labels[j], bbox=det_bboxes[j])
                    t.history.append((int(cx*WIDTH/CAP_W), int(cy*HEIGHT/CAP_H)))
                    self.tracks.append(t)
                    self.next_id += 1

            # Aging and confirmation
            survivors = []
            for i, tr in enumerate(self.tracks):
                if i not in matched_tracks:
                    tr.time_since_update += 1
                tr.confirmed = (tr.hits >= self.confirm_N)
                if tr.time_since_update <= self.max_age:
                    survivors.append(tr)
            self.tracks = survivors

        else:
            # No current tracks or no detections -> create new from detections
            for j in range(D):
                if len(self.tracks) < self.max_tracks:
                    cx, cy = det_centers[j]
                    t = KalmanTrack(self.next_id, cx, cy, Q_scale=self.Q_scale, R_scale=self.R_scale,
                                    label=det_labels[j], bbox=det_bboxes[j])
                    t.history.append((int(cx*WIDTH/CAP_W), int(cy*HEIGHT/CAP_H)))
                    self.tracks.append(t); self.next_id += 1

            # Age tracks if no detections
            if D == 0:
                self.tracks = [t for t in self.tracks if t.time_since_update <= self.max_age]

        return self.tracks

# -----------------------------
# Target scoring & selection
# -----------------------------
def target_score(track, center=(WIDTH//2, HEIGHT//2)):
    # Confidence: face gets bonus, confirmed tracks favored, recency matters
    face_bonus = 20.0 if (track.label == "face") else 0.0
    confirmed_bonus = 10.0 if track.confirmed else 0.0

    area = 0.0
    if track.last_bbox is not None:
        x,y,w,h = track.last_bbox
        area = w*h

    cx, cy = track.get_position()
    cx_disp = int(cx * WIDTH / CAP_W)
    cy_disp = int(cy * HEIGHT / CAP_H)
    dist_center = math.hypot(cx_disp - center[0], cy_disp - center[1])

    recent_penalty = track.time_since_update * 6.0
    age_bonus = min(track.hits*2.0, 30.0)

    # Motion magnitude
    vx, vy = track.get_velocity()
    motion_mag = math.hypot(vx, vy)

    # Score
    score = (area*0.05) + face_bonus + confirmed_bonus + age_bonus \
            + (motion_mag*8.0) - (dist_center*0.25) - recent_penalty
    return score

def pick_target(tracks, mouse_pos, locked_ids, current_lock_index):
    # Priority: locked attacker -> selected locked -> best unlocked
    if locked_ids:
        # Attacker among locked
        for tid in locked_ids:
            t = next((tr for tr in tracks if tr.id == tid), None)
            if t:
                vx, vy = t.get_velocity()
                cx, cy = t.get_position()
                cx_disp = int(cx * WIDTH / CAP_W); cy_disp = int(cy * HEIGHT / CAP_H)
                dx = (WIDTH//2) - cx_disp; dy = (HEIGHT//2) - cy_disp
                if vx*dx + vy*dy > 0:  # moving toward center
                    return t
        # Cycle locked
        tid = locked_ids[current_lock_index % len(locked_ids)]
        return next((tr for tr in tracks if tr.id == tid), None)

    # No locks: bias by mouse and score
    mx, my = mouse_pos
    best, bests = None, -1e9
    for t in tracks:
        cx, cy = t.get_position()
        cx_disp = int(cx * WIDTH / CAP_W); cy_disp = int(cy * HEIGHT / CAP_H)
        dist_mouse = math.hypot(mx - cx_disp, my - cy_disp)
        s = target_score(t) - dist_mouse*0.25
        if s > bests:
            bests = s; best = t
    return best

# -----------------------------
# Reticle
# -----------------------------
class Reticle:
    def __init__(self):
        self.pos = np.array([WIDTH//2, HEIGHT//2], dtype=np.float32)
        self.alpha = 0.22  # smoothing
        self.snap_gain = 0.06  # quick snap

    def update(self, t):
        center = np.array([WIDTH//2, HEIGHT//2], dtype=np.float32)
        if t is None:
            self.pos = (1-self.alpha)*self.pos + self.alpha*center
            return
        cx, cy = t.get_position(); vx, vy = t.get_velocity()
        cx_disp = cx*WIDTH/CAP_W; cy_disp = cy*HEIGHT/CAP_H
        # Predictive lead
        tx = cx_disp + vx*(WIDTH/CAP_W)*0.035
        ty = cy_disp + vy*(HEIGHT/CAP_H)*0.035
        target = np.array([tx, ty], dtype=np.float32)
        # Blend snap and smooth
        self.pos = self.pos + self.snap_gain*(target - self.pos)
        self.pos = (1-self.alpha)*self.pos + self.alpha*target

    def draw(self, surf):
        x, y = int(self.pos[0]), int(self.pos[1])
        pygame.draw.line(surf, YELLOW, (x-12,y), (x+12,y), 2)
        pygame.draw.line(surf, YELLOW, (x,y-12), (x,y+12), 2)
        pygame.draw.circle(surf, YELLOW, (x,y), 16, 1)

# -----------------------------
# Sliders (sensitivity & stability)
# -----------------------------
class Slider:
    def __init__(self, x, y, w, label, init=0.5):
        self.rect = pygame.Rect(x, y, w, 10)
        self.handle_x = x + int(init * w)
        self.label = label
        self.value = init
        self.dragging = False

    def handle_event(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(event.pos) or abs(event.pos[0]-self.handle_x) < 10:
                self.dragging = True
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.dragging = False
        elif event.type == pygame.MOUSEMOTION and self.dragging:
            x = np.clip(event.pos[0], self.rect.x, self.rect.x + self.rect.width)
            self.handle_x = int(x)
            self.value = (self.handle_x - self.rect.x) / self.rect.width

    def draw(self, surf):
        pygame.draw.rect(surf, WHITE, self.rect, 1)
        pygame.draw.rect(surf, BLUE, (self.rect.x, self.rect.y+4, self.handle_x - self.rect.x, 2))
        pygame.draw.circle(surf, CYAN, (self.handle_x, self.rect.y+5), 6)
        text = font.render(f"{self.label}: {self.value:.2f}", True, WHITE)
        surf.blit(text, (self.rect.x, self.rect.y - 18))

# -----------------------------
# Main loop
# -----------------------------
confirm_N, max_age, gate_mahal, Q_scale, R_scale = tracking_params_from_stability(stability)
tracker = MultiTrackerHungarian(max_age=max_age, confirm_N=confirm_N, gate_mahal=gate_mahal,
                                Q_scale=Q_scale, R_scale=R_scale)
reticle = Reticle()
locked_ids = []
current_lock_index = 0
click_indicator_pos = None
click_indicator_timer = 0
LOCK_THRESHOLD = 30
mouse_pos = (WIDTH//2, HEIGHT//2)

slider_sens = Slider(10, HEIGHT-40, 240, "Sensitivity", init=sensitivity)
slider_stab = Slider(270, HEIGHT-40, 240, "Stability",   init=stability)

try:
    while True:
        # --- Event handling ---
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt
            elif event.type == pygame.MOUSEMOTION:
                mouse_pos = event.pos
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mx, my = pygame.mouse.get_pos()
                if event.button == 1:
                    click_indicator_pos = (mx, my); click_indicator_timer = 15
                    closest_id, min_dist = None, float('inf')
                    for t in tracker.tracks:
                        cx, cy = t.get_position()
                        cx_disp = int(cx * WIDTH / CAP_W); cy_disp = int(cy * HEIGHT / CAP_H)
                        dist = math.hypot(mx - cx_disp, my - cy_disp)
                        if dist < min_dist:
                            min_dist = dist; closest_id = t.id
                    if closest_id is not None and min_dist <= LOCK_THRESHOLD:
                        if closest_id not in locked_ids:
                            locked_ids.append(closest_id)
                        logging.info(f"Locked target ID {closest_id}")
                elif event.button == 3:
                    locked_ids.clear(); click_indicator_pos = None; click_indicator_timer = 0
                    logging.info("Cleared all locks")
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_TAB and locked_ids:
                    current_lock_index = (current_lock_index + 1) % len(locked_ids)
                    logging.info(f"Cycled to locked target ID {locked_ids[current_lock_index]}")

            # Sliders
            slider_sens.handle_event(event)
            slider_stab.handle_event(event)

        # Update tunables from sliders
        sensitivity = slider_sens.value
        stability   = slider_stab.value
        confirm_N, max_age, gate_mahal, Q_scale, R_scale = tracking_params_from_stability(stability)
        # If stability changed significantly, we could re-init tracker. For simplicity, update fields.
        tracker.confirm_N = confirm_N
        tracker.max_age   = max_age
        tracker.gate_mahal= gate_mahal
        tracker.Q_scale   = Q_scale
        tracker.R_scale   = R_scale

        # --- Frame capture ---
        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            clock.tick(30); continue

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # --- Detections ---
        detections_faces  = detect_faces(gray)
        detections_motion = detect_motion(frame, sensitivity)

        # Fuse detections with simple de-duplication (face dominates motion if IoU high)
        detections = list(detections_faces)  # start with faces
        for label, mb in detections_motion:
            duplicate = False
            for _, fb in detections_faces:
                if iou(mb, fb) > 0.5:
                    duplicate = True
                    break
            if not duplicate:
                detections.append((label, mb))

        # --- Tracking ---
        tracks = tracker.step(detections)

        # --- Target selection ---
        target_track = pick_target(tracks, mouse_pos, locked_ids, current_lock_index)
        reticle.update(target_track)

        # --- Drawing video ---
        vis = cv2.resize(frame, (WIDTH, HEIGHT))
        rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
        arr = np.transpose(rgb, (1,0,2)).copy()
        pygame.surfarray.blit_array(display_surface, arr)
        screen.blit(display_surface, (0,0))

        # --- Draw tracks ---
        for t in tracks:
            cx, cy = t.get_position()
            cx_disp = int(cx * WIDTH / CAP_W); cy_disp = int(cy * HEIGHT / CAP_H)
            color = BLUE if (t.label == "face") else ORANGE
            pygame.draw.circle(screen, color, (cx_disp, cy_disp), 6)
            lbl = f"{(t.label or 'ID').upper()} {t.id}{' ✓' if t.confirmed else ''}"
            screen.blit(font.render(lbl, True, WHITE), (cx_disp+8, cy_disp-18))
            for i in range(1, len(t.history)):
                pygame.draw.line(screen, color, t.history[i-1], t.history[i], 2)

        # --- Highlight locked targets ---
        for idx, tid in enumerate(locked_ids):
            t = next((tr for tr in tracks if tr.id == tid), None)
            if t:
                cx, cy = t.get_position()
                cx_disp = int(cx * WIDTH / CAP_W); cy_disp = int(cy * HEIGHT / CAP_H)
                color_ring = GREEN if idx != current_lock_index else YELLOW
                pygame.draw.circle(screen, color_ring, (cx_disp, cy_disp), 12, 2)
                screen.blit(font.render(f"LOCKED {tid}", True, color_ring), (cx_disp+12, cy_disp-24))

        # --- Attacking marker (flashing red outline) ---
        ticks = pygame.time.get_ticks()
        flash_on = (ticks // 300) % 2 == 0
        if flash_on:
            for t in tracks:
                vx, vy = t.get_velocity()
                cx, cy = t.get_position()
                cx_disp = int(cx * WIDTH / CAP_W); cy_disp = int(cy * HEIGHT / CAP_H)
                dx = (WIDTH//2) - cx_disp; dy = (HEIGHT//2) - cy_disp
                if vx*dx + vy*dy > 0:  # moving toward center
                    pygame.draw.circle(screen, RED, (cx_disp, cy_disp), 16, 3)
                    screen.blit(font.render("ATTACKING", True, RED), (cx_disp+14, cy_disp-28))

        # --- Reticle ---
        reticle.draw(screen)

        # --- Click indicator ---
        if click_indicator_timer > 0 and click_indicator_pos is not None:
            pygame.draw.circle(screen, YELLOW, click_indicator_pos, LOCK_THRESHOLD, 2)
            click_indicator_timer -= 1

        # --- HUD & sliders ---
        fps = clock.get_fps()
        status = f"FPS: {fps:.1f} | Tracks: {len(tracks)} | Dets: {len(detections)} | Locks: {locked_ids if locked_ids else 'Auto'}"
        screen.blit(font.render(status, True, WHITE), (10, 10))

        slider_sens.draw(screen)
        slider_stab.draw(screen)

        pygame.display.flip()
        clock.tick(30)

except KeyboardInterrupt:
    logging.info("Stopped by user")
finally:
    cap.release(); pygame.quit(); sys.exit()

