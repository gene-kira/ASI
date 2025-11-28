import cv2
import numpy as np
import pygame
import torch
import torch.nn as nn
import torch.optim as optim
from collections import deque
import logging
import sys
import math
import time

# -----------------------------
# Logging (throttled)
# -----------------------------
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s %(levelname)s: %(message)s')

def log_periodic(msg, period=2.0, state={'last': 0.0}):
    now = time.time()
    if now - state['last'] >= period:
        logging.info(msg)
        state['last'] = now

# -----------------------------
# GUI setup
# -----------------------------
WIDTH, HEIGHT = 800, 600
WHITE, RED, GREEN, BLUE = (255,255,255), (255,0,0), (0,255,0), (0,0,255)

pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Stable Autonomous Tracker (Safe Mode)")
clock = pygame.time.Clock()
font = pygame.font.Font(None, 22)

# Preallocated display surface to avoid churn
display_surface = pygame.Surface((WIDTH, HEIGHT))

# -----------------------------
# Camera (guarded)
# -----------------------------
cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)   # smaller processing resolution
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 360)
cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)

if not cap.isOpened():
    print("Failed to open camera.")
    logging.error("Failed to open camera.")
    pygame.quit()
    sys.exit(1)

# -----------------------------
# Haar Cascade (faces only for stability)
# -----------------------------
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

def detect_faces(frame_gray):
    faces = face_cascade.detectMultiScale(frame_gray, scaleFactor=1.1, minNeighbors=5, minSize=(30, 30))
    return [("face", (x, y, w, h)) for (x, y, w, h) in faces]

# -----------------------------
# Utility
# -----------------------------
def clamp_point(x, y, w=WIDTH, h=HEIGHT):
    return max(0, min(w-1, int(x))), max(0, min(h-1, int(y)))

# -----------------------------
# Kalman filter track (constant velocity)
# -----------------------------
class KalmanTrack:
    def __init__(self, track_id, cx, cy):
        self.id = track_id
        self.x = np.array([[cx],[cy],[0.0],[0.0]], dtype=np.float32)
        self.P = np.eye(4, dtype=np.float32) * 50.0
        self.Q = np.eye(4, dtype=np.float32) * 1.0
        self.R = np.eye(2, dtype=np.float32) * 5.0
        self.H = np.array([[1,0,0,0],[0,1,0,0]], dtype=np.float32)
        self.last_update_time = time.time()
        self.age = 0
        self.time_since_update = 0
        self.history = deque(maxlen=16)
        self.label = "face"

    def F(self, dt):
        return np.array([[1,0,dt,0],
                         [0,1,0,dt],
                         [0,0,1,0],
                         [0,0,0,1]], dtype=np.float32)

    def predict(self, dt=1/30.0):
        Fm = self.F(dt)
        self.x = Fm @ self.x
        self.P = Fm @ self.P @ Fm.T + self.Q
        self.age += 1
        self.time_since_update += 1
        return float(self.x[0,0]), float(self.x[1,0])

    def update(self, z):
        z = np.array(z, dtype=np.float32).reshape(2,1)
        y = z - (self.H @ self.x)
        S = self.H @ self.P @ self.H.T + self.R
        try:
            K = self.P @ self.H.T @ np.linalg.inv(S)
        except np.linalg.LinAlgError:
            S = S + np.eye(2, dtype=np.float32) * 1e-3
            K = self.P @ self.H.T @ np.linalg.inv(S)
        self.x = self.x + K @ y
        I = np.eye(4, dtype=np.float32)
        self.P = (I - K @ self.H) @ self.P
        self.time_since_update = 0
        self.last_update_time = time.time()

    def get_position(self):
        return float(self.x[0,0]), float(self.x[1,0])

# -----------------------------
# Greedy tracker (no scipy)
# -----------------------------
class GreedyMultiTracker:
    def __init__(self, max_age=12, dist_threshold=80.0, max_tracks=16):
        self.tracks = []
        self.next_id = 0
        self.max_age = max_age
        self.dist_threshold = dist_threshold
        self.dt = 1/30.0
        self.max_tracks = max_tracks

    def _distance(self, tpos, dpos):
        tx, ty = tpos
        dx, dy = dpos
        return math.hypot(tx - dx, ty - dy)

    def step(self, detections):
        # Predict all tracks forward
        for t in self.tracks:
            t.predict(self.dt)

        # Prepare detection centers
        det_centers = []
        for _, (x, y, w, h) in detections:
            det_centers.append((x + w / 2.0, y + h / 2.0))

        # Greedy assignment: for each det, find nearest track under threshold
        used_tracks = set()
        for di, (cx, cy) in enumerate(det_centers):
            best_ti = None
            best_dist = float('inf')
            for ti, t in enumerate(self.tracks):
                if ti in used_tracks:
                    continue
                tx, ty = t.get_position()
                dist = self._distance((tx, ty), (cx, cy))
                if dist < best_dist:
                    best_dist = dist
                    best_ti = ti
            if best_ti is not None and best_dist <= self.dist_threshold:
                # Update matched track
                self.tracks[best_ti].update([cx, cy])
                cxc, cyc = clamp_point(cx, cy, WIDTH, HEIGHT)
                self.tracks[best_ti].history.append((cxc, cyc))
                used_tracks.add(best_ti)
            else:
                # Create new track if under cap
                if len(self.tracks) < self.max_tracks:
                    t = KalmanTrack(self.next_id, cx, cy)
                    cxc, cyc = clamp_point(cx, cy, WIDTH, HEIGHT)
                    t.history.append((cxc, cyc))
                    self.tracks.append(t)
                    self.next_id += 1

        # Remove stale or stagnant tracks
        alive = []
        for t in self.tracks:
            stagnant = (len(t.history) >= 5 and len(set(t.history)) == 1)
            if t.time_since_update <= self.max_age and not stagnant:
                alive.append(t)
        self.tracks = alive

        return self.tracks

# -----------------------------
# Optional Transformer (disabled by default)
# -----------------------------
ENABLE_TRANSFORMER = False       # set True to enable prediction
PREDICT_EVERY_N_FRAMES = 5       # reduce overhead
HISTORY_LEN = 10

class PositionalEncoding(nn.Module):
    def __init__(self, d_model, max_len=5000):
        super().__init__()
        pe = torch.zeros(max_len, d_model)
        position = torch.arange(0, max_len, dtype=torch.float).unsqueeze(1)
        div_term = torch.exp(torch.arange(0, d_model, 2).float() * (-np.log(10000.0) / d_model))
        pe[:, 0::2] = torch.sin(position * div_term)
        pe[:, 1::2] = torch.cos(position * div_term)
        self.register_buffer('pe', pe.unsqueeze(1))
    def forward(self, x):
        return x + self.pe[:x.size(0)]

class TransformerPredictor(nn.Module):
    def __init__(self, d_model=64, nhead=8, num_encoder_layers=2, dim_feedforward=256, dropout=0.1):
        super().__init__()
        self.input_proj = nn.Linear(2, d_model)
        self.positional_encoding = PositionalEncoding(d_model)
        enc_layer = nn.TransformerEncoderLayer(d_model, nhead, dim_feedforward, dropout, batch_first=False)
        self.encoder = nn.TransformerEncoder(enc_layer, num_encoder_layers)
        self.linear_out = nn.Linear(d_model, 2)
    def forward(self, src):
        src = self.input_proj(src)
        src = self.positional_encoding(src)
        enc = self.encoder(src)
        return self.linear_out(enc[-1])

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
if ENABLE_TRANSFORMER:
    model = TransformerPredictor().to(device)
    criterion = nn.MSELoss()
    optimizer = optim.Adam(model.parameters(), lr=1e-3)

def predict_next(seq_points):
    x = torch.tensor(seq_points, dtype=torch.float32, device=device).unsqueeze(1)
    with torch.no_grad():
        pred = model(x)
    return pred.squeeze(0).cpu().numpy().tolist()

# -----------------------------
# Main loop
# -----------------------------
tracker = GreedyMultiTracker(max_age=10, dist_threshold=70.0, max_tracks=12)
predicted_points = {}  # track_id -> deque of predicted points
frame_count = 0

try:
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                raise KeyboardInterrupt

        ret, frame = cap.read()
        if not ret or frame is None or frame.size == 0:
            logging.warning("Invalid frame; skipping.")
            clock.tick(30)
            continue

        # Detection on grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        detections = detect_faces(gray)

        # Step tracker
        tracks = tracker.step(detections)

        # Optional prediction
        frame_count += 1
        if ENABLE_TRANSFORMER and (frame_count % PREDICT_EVERY_N_FRAMES == 0):
            for t in tracks:
                if t.id not in predicted_points:
                    predicted_points[t.id] = deque(maxlen=32)
                if len(t.history) >= HISTORY_LEN and len(set(t.history)) > 1:
                    seq = list(t.history)[-HISTORY_LEN:]
                    try:
                        px, py = predict_next(seq)
                        px, py = clamp_point(px, py, WIDTH, HEIGHT)
                        predicted_points[t.id].append((int(px), int(py)))
                    except Exception as e:
                        logging.warning(f"Transformer predict error on track {t.id}: {e}")

        # Draw frame into preallocated surface (avoid churn)
        vis = cv2.resize(frame, (WIDTH, HEIGHT))
        rgb = cv2.cvtColor(vis, cv2.COLOR_BGR2RGB)
        # surfarray expects shape (w,h,3) and contiguous array; transpose from (h,w,3)
        arr = np.transpose(rgb, (1, 0, 2)).copy()
        try:
            pygame.surfarray.blit_array(display_surface, arr)
            screen.blit(display_surface, (0, 0))
        except Exception as e:
            logging.warning(f"Blit error: {e}")
            # Fallback
            surf = pygame.image.frombuffer(rgb.tobytes(), (WIDTH, HEIGHT), "RGB")
            screen.blit(surf, (0, 0))
            del surf

        # Render tracks and histories
        for t in tracks:
            cx, cy = t.get_position()
            cx, cy = clamp_point(cx, cy, WIDTH, HEIGHT)
            pygame.draw.circle(screen, RED, (cx, cy), 6)
            screen.blit(font.render(f"ID {t.id}", True, BLUE), (cx + 8, cy - 18))
            hist_list = list(t.history)
            for i in range(1, len(hist_list)):
                pygame.draw.line(screen, RED, hist_list[i-1], hist_list[i], 2)

            # Optional predicted points
            preds = predicted_points.get(t.id, [])
            if ENABLE_TRANSFORMER and len(preds) > 1:
                for i in range(1, len(preds)):
                    pygame.draw.line(screen, BLUE, preds[i-1], preds[i], 2)
                px, py = preds[-1]
                pygame.draw.circle(screen, BLUE, (px, py), 5)

        fps = clock.get_fps()
        status = f"FPS: {fps:.1f} | Tracks: {len(tracks)} | Dets: {len(detections)}"
        screen.blit(font.render(status, True, GREEN), (10, 10))
        pygame.display.flip()
        clock.tick(30)
        log_periodic(status, period=3.0)

except KeyboardInterrupt:
    logging.info("Stopped by user")
finally:
    cap.release()
    pygame.quit()
    sys.exit()

