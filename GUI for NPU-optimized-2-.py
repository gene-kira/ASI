# MagicBox: Real-Time GlyphCore Dashboard
# Author: killer666 + Copilot

import os, sys, subprocess, threading, json
import tkinter as tk
from tkinter import ttk
import cv2
import numpy as np
from PIL import Image, ImageTk, ImageDraw

# 🔄 Auto-loader
REQUIRED_LIBS = ['cv2', 'numpy', 'PIL']
def autoload_libraries():
    for lib in REQUIRED_LIBS:
        try: __import__(lib)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
autoload_libraries()

# 📜 Load symbolic overlays from config
def load_overlay_config(path="overlay_config.json"):
    if not os.path.exists(path):
        return {"glyph": "🌀", "color": "#00f", "trail": ["→", "↻", "★"]}
    with open(path, "r") as f:
        return json.load(f)

# 🎥 Real-time camera stream
class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0)
        self.running = False

    def get_frame(self):
        if not self.cap.isOpened(): return None
        ret, frame = self.cap.read()
        if not ret: return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame)

    def release(self):
        if self.cap: self.cap.release()

# 🧙‍♂️ GUI
class MagicBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧙‍♂️ MagicBox: Real-Time GlyphCore")
        self.root.geometry("800x600")
        self.root.configure(bg="#1e1e2f")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Helvetica", 14), padding=10, background="#444", foreground="#fff")
        style.map("TButton", background=[("active", "#666")])

        self.overlay_config = load_overlay_config()
        self.camera = CameraStream()

        self.canvas = tk.Canvas(root, width=800, height=480, bg="#000", highlightthickness=0)
        self.canvas.pack()

        self.button = ttk.Button(root, text="🌀 Activate GlyphCore", command=self.activate_glyphcore)
        self.button.pack(pady=10)

        self.status = tk.Label(root, text="Ready", font=("Helvetica", 12), bg="#1e1e2f", fg="#aaa")
        self.status.pack()

        self.running = False
        self.previous_frame = None

    def activate_glyphcore(self):
        self.status.config(text="Running...")
        self.running = True
        threading.Thread(target=self.update_stream).start()

    def update_stream(self):
        while self.running:
            frame = self.camera.get_frame()
            if frame:
                draw = ImageDraw.Draw(frame)
                glyph = self.overlay_config.get("glyph", "🌀")
                color = self.overlay_config.get("color", "#00f")
                trail = self.overlay_config.get("trail", ["→", "↻", "★"])

                # 🌀 Overlay glyphs
                draw.text((10, 10), glyph, fill=color)
                for i, t in enumerate(trail):
                    draw.text((10 + i*30, 40), t, fill=color)

                # 🔗 Real-time sync visualization based on frame delta
                current_np = np.array(frame.convert("L"))
                if self.previous_frame is not None:
                    delta = np.mean(np.abs(current_np - self.previous_frame))
                    sync_status = "Stable 🔗" if delta < 5 else "Mutating ⚠️"
                    draw.text((10, 80), f"Sync: {sync_status}", fill="#0f0" if delta < 5 else "#f00")
                self.previous_frame = current_np

                # 🖼️ Update canvas
                img_tk = ImageTk.PhotoImage(frame.resize((800, 480)))
                self.canvas.create_image(0, 0, anchor=tk.NW, image=img_tk)
                self.canvas.image = img_tk
            self.root.update_idletasks()
            self.root.after(30)

    def stop(self):
        self.running = False
        self.camera.release()

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxApp(root)
    root.protocol("WM_DELETE_WINDOW", app.stop)
    root.mainloop()

