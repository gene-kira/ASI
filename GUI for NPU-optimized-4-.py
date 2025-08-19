import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageDraw
import numpy as np

class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)
        if not self.cap.isOpened():
            raise RuntimeError("❌ Camera not detected. Please check your webcam connection.")

    def get_frame(self):
        ret, frame = self.cap.read()
        if not ret or frame is None:
            return None
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        return Image.fromarray(frame)

    def release(self):
        if self.cap and self.cap.isOpened():
            self.cap.release()

class MagicBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🎯 MagicBox: AI Targeting Edition")
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

        self.status = tk.Label(root, text="🔍 Scanning...", fg="lime", bg="#1e1e2f", font=("Consolas", 14))
        self.status.pack(pady=10)

        self.previous_gray = None
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

                targets = [cv2.boundingRect(c) for c in contours if cv2.contourArea(c) > 500]
                for (x, y, w, h) in targets:
                    draw.rectangle([x, y, x+w, y+h], outline="red", width=2)
                    draw.text((x, y-20), "🎯", fill="red")

                self.status.config(text=f"Targets: {len(targets)}")

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

