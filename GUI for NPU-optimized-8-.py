import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np
import socket
import json
import time

# --- Game AI Sync ---
class GameAISync:
    def __init__(self, host='localhost', port=5555):
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.addr = (host, port)

    def send(self, data):
        payload = json.dumps(data).encode('utf-8')
        self.sock.sendto(payload, self.addr)

# --- Learning Memory Map ---
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

# --- Glyph Overlay ---
class GlyphOverlay:
    @staticmethod
    def render(draw, box, score):
        x, y, w, h = box
        color = "red" if score > 0.7 else "orange" if score > 0.4 else "yellow"
        glyph = "🎯"
        draw.rectangle([x, y, x+w, y+h], outline=color, width=2)
        draw.text((x, y-20), f"{glyph} {int(score*100)}%", fill=color)

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
        return frame

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

# --- Main App ---
class MagicBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MagicBox v4.0: Motion-Based Mythic Engine")
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
        self.game_sync = GameAISync()
        self.root.after(10, self.update_frame)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        raw = self.camera.get_frame()
        if raw is not None:
            gray = cv2.cvtColor(raw, cv2.COLOR_BGR2GRAY)
            frame_rgb = cv2.cvtColor(raw, cv2.COLOR_BGR2RGB)
            pil_img = Image.fromarray(frame_rgb)
            draw = ImageDraw.Draw(pil_img)

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
                    GlyphOverlay.render(draw, (x, y, w, h), score)

                    self.game_sync.send({
                        "target_id": i,
                        "score": round(score, 2),
                        "position": center,
                        "glyph": "🔥" if score > 0.8 else "⚠️" if score > 0.5 else "🌀"
                    })

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

