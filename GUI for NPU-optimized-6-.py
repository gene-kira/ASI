import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import socket
import json

# --- Threat Scoring Engine ---
class ThreatScorer:
    @staticmethod
    def evaluate(contour, delta_frame):
        x, y, w, h = cv2.boundingRect(contour)
        roi = delta_frame[y:y+h, x:x+w]
        entropy = np.sum(roi) / (w * h + 1)
        velocity = cv2.contourArea(contour) / (w * h + 1)
        score = min(1.0, (entropy + velocity) / 255)
        return score

# --- Predictive Routing Engine ---
class PredictiveRouter:
    @staticmethod
    def route(history):
        if len(history) < 2:
            return None
        dx = history[-1][0] - history[-2][0]
        dy = history[-1][1] - history[-2][1]
        return (dx, dy)

# --- Glyph Overlay ---
class TargetGlyphOverlay:
    @staticmethod
    def render(draw, x, y, w, h, score, direction):
        color = "red" if score > 0.7 else "orange" if score > 0.4 else "yellow"
        draw.rectangle([x, y, x+w, y+h], outline=color, width=2)
        draw.text((x, y-20), f"🎯 {int(score*100)}%", fill=color)
        if direction:
            dx, dy = direction
            draw.line([x+w//2, y+h//2, x+w//2+dx*5, y+h//2+dy*5], fill=color, width=2)

# --- VaultSyncEngine Stub ---
class VaultSyncEngine:
    @staticmethod
    def sync(target_id, score, position):
        pass  # Placeholder for encrypted memory sync

# --- MutationTrailRenderer Stub ---
class MutationTrailRenderer:
    @staticmethod
    def draw(draw, history):
        for (x, y) in history:
            draw.ellipse([x-2, y-2, x+2, y+2], fill="cyan")

# --- Game AI Sync ---
class GameAISync:
    def __init__(self, host='localhost', port=5555):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (host, port)

    def send(self, data):
        payload = json.dumps(data).encode('utf-8')
        self.sock.sendto(payload, self.addr)

# --- Camera Stream ---
class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("❌ Camera not detected.")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame)

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

# --- Main App ---
class MagicBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MagicBox v3.0: Mythic Threat Engine")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2f")

        try:
            self.camera = CameraStream()
        except RuntimeError as e:
            messagebox.showerror("Camera Error", str(e))
            self.status = tk.Label(root, text="Camera not available ❌", fg="red", bg="#1e1e2f", font=("Consolas", 14))
            self.status.pack(pady=20)
            return

        self.canvas = tk.Label(root)
        self.canvas.pack(expand=True)

        self.status = tk.Label(root, text="🌀 Initializing Mythic Engine...", fg="lime", bg="#1e1e2f", font=("Consolas", 14))
        self.status.pack(pady=10)

        self.previous_gray = None
        self.target_histories = {}
        self.game_sync = GameAISync()
        self.root.after(10, self.update_frame)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame:
            gray = np.array(frame.convert("L"))
            draw = ImageDraw.Draw(frame)

            if self.previous_gray is not None:
                delta = cv2.absdiff(gray, self.previous_gray)
                thresh = cv2.threshold(delta, 25, 255, cv2.THRESH_BINARY)[1]
                contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

                targets = [c for c in contours if cv2.contourArea(c) > 500]
                for i, contour in enumerate(targets):
                    x, y, w, h = cv2.boundingRect(contour)
                    center = (x + w // 2, y + h // 2)

                    score = ThreatScorer.evaluate(contour, delta)
                    history = self.target_histories.get(i, [])
                    history.append(center)
                    self.target_histories[i] = history[-10:]

                    direction = PredictiveRouter.route(history)
                    TargetGlyphOverlay.render(draw, x, y, w, h, score, direction)
                    MutationTrailRenderer.draw(draw, history)
                    VaultSyncEngine.sync(i, score, center)

                    glyph = "🔥" if score > 0.8 else "⚠️" if score > 0.5 else "🌀"
                    self.game_sync.send({
                        "target_id": i,
                        "score": round(score, 2),
                        "position": center,
                        "direction": direction if direction else [0, 0],
                        "glyph": glyph
                    })

                self.status.config(text=f"🎯 Targets: {len(targets)}")

            self.previous_gray = gray
            img = ImageTk.PhotoImage(image=frame)
            self.canvas.configure(image=img)
            self.canvas.image = img
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

