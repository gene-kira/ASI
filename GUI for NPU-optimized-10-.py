import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import socket
import json
import time
import requests
import hashlib
import urllib.request

# --- WebhookSync ---
class WebhookSync:
    def __init__(self, url):
        self.url = url

    def send(self, payload):
        try:
            requests.post(self.url, json=payload, timeout=2)
        except Exception as e:
            print("Webhook error:", e)

# --- RemoteStreamSync ---
class RemoteStreamSync:
    def __init__(self, host='remote.server.com', port=6000):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (host, port)

    def stream(self, data):
        try:
            self.sock.sendto(json.dumps(data).encode(), self.addr)
        except Exception as e:
            print("Stream error:", e)

# --- VaultSyncEngine ---
class VaultSyncEngine:
    def __init__(self, node_id):
        self.node_id = node_id
        self.vault = {}

    def sync(self, label, score, position):
        key = hashlib.sha256(f"{label}:{position}".encode()).hexdigest()
        self.vault[key] = {
            "score": score,
            "position": position,
            "timestamp": time.time()
        }

# --- TargetTracker ---
class TargetTracker:
    def __init__(self):
        self.locked_target = None
        self.last_position = None

    def select_target(self, positions, scores):
        if not positions:
            self.locked_target = None
            return None
        best_index = int(np.argmax(scores))
        self.locked_target = best_index
        return positions[best_index]

    def get_aim_vector(self, current_position):
        if self.last_position is None:
            self.last_position = current_position
            return (0, 0)
        dx = current_position[0] - self.last_position[0]
        dy = current_position[1] - self.last_position[1]
        self.last_position = current_position
        return (dx, dy)

# --- MemoryMap ---
class MemoryMap:
    def __init__(self):
        self.memory = {}

    def update(self, target_id, position):
        now = time.time()
        if target_id not in self.memory:
            self.memory[target_id] = {"last_seen": now, "count": 1, "positions": [position]}
        else:
            self.memory[target_id]["last_seen"] = now
            self.memory[target_id]["count"] += 1
            self.memory[target_id]["positions"].append(position)

    def get_threat_score(self, target_id):
        data = self.memory.get(target_id, {})
        count = data.get("count", 1)
        recency = time.time() - data.get("last_seen", 0)
        score = min(1.0, (count / 10.0) * (1.0 if recency < 5 else 0.5))
        return score

# --- GlyphOverlay ---
class GlyphOverlay:
    @staticmethod
    def render(draw, box, score, locked=False, aim_vector=None):
        x, y, w, h = box
        color = "red" if score > 0.7 else "orange" if score > 0.4 else "yellow"
        glyph = "🎯" if locked else "🌀"
        draw.rectangle([x, y, x+w, y+h], outline=color, width=2)
        draw.text((x, y-20), f"{glyph} {int(score*100)}%", fill=color)
        if aim_vector:
            dx, dy = aim_vector
            draw.line([x+w//2, y+h//2, x+w//2+dx*5, y+h//2+dy*5], fill=color, width=2)

# --- CameraStream ---
class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("❌ Camera not detected.")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        return frame

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

# --- Main App ---
class MagicBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MagicBox v6.0: Auto-Lock Swarm Node")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2f")

        try:
            self.camera = CameraStream()
        except Exception as e:
            messagebox.showerror("Initialization Error", str(e))
            self.status = tk.Label(root, text="Initialization failed ❌", fg="red", bg="#1e1e2f", font=("Consolas", 14))
            self.status.pack(pady=20)
            return

        self.canvas = tk.Label(root)
        self.canvas.pack(expand=True)

        self.status = tk.Label(root, text="🌀 Mythic Engine Ready", fg="lime", bg="#1e1e2f", font=("Consolas", 14))
        self.status.pack(pady=10)

        self.previous_gray = None
        self.memory = MemoryMap()
        self.webhook = WebhookSync("https://your-dashboard-endpoint.com/webhook")
        self.streamer = RemoteStreamSync()
        self.vault = VaultSyncEngine(node_id="node-001")
        self.tracker = TargetTracker()

        self.root.after(10, self.update_frame)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        raw = self.camera.get_frame()
        if raw is not None:
            gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
            frame_rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            draw = ImageDraw.Draw(pil_img)

            positions = []
            scores = []
            boxes = []

            if self.previous_gray is not None:
                delta = cv2.absdiff(gray, self.previous_gray)
                thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                targets = [c for c in contours if cv2.contourArea(c) > 500]
                for i, contour in enumerate(targets):
                    x, y, w, h = cv2.boundingRect(contour)
                    center = (x + w // 2, y + h // 2)
                    self.memory.update(i, center)
                    score = self.memory.get_threat_score(i)

                    positions.append(center)
                    scores.append(score)
                    boxes.append((x, y, w, h))

                locked_position = self.tracker.select_target(positions, scores)
                aim_vector = self.tracker.get_aim_vector(locked_position) if locked_position else None

                for i, box in enumerate(boxes):
                    locked = (i == self.tracker.locked_target)
                    GlyphOverlay.render(draw, box, scores[i], locked=locked, aim_vector=aim_vector if locked else None)

                    payload = {
                        "target_id": i,
                        "score": round(scores[i], 2),
                        "position": positions[i],
                        "locked": locked,
                        "aim_vector": aim_vector if locked else (0, 0),
                        "glyph": "🔥" if scores[i] > 0.8 else "⚠️" if scores[i] > 0.5 else "🌀"
                    }

                    self.webhook.send(payload)
                    self.streamer.stream(payload)
                    self.vault.sync(f"target-{i}", scores[i], positions[i])

                self.status.config(text=f"🎯 Targets detected: {len(targets)}")

            self.previous_gray = gray
            img_tk = ImageTk.PhotoImage(pil_img)
            self.canvas.configure(image=img_tk)
            self.canvas.image = img_tk
        else:
            self.status.config(text="⚠️ Frame error")
        self.root.after(30, self.update_frame)

    def on_close(self):
        if hasattr(self, 'camera'):
            self.camera.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxApp(root)
    root.mainloop()

