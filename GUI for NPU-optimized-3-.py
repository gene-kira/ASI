import cv2
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk

class CameraStream:
    def __init__(self):
        self.cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)  # Use DirectShow for better Windows compatibility
        self.running = False
        if not self.cap.isOpened():
            raise RuntimeError("❌ Camera not detected. Please check your webcam connection.")

    def get_frame(self):
        if not self.cap.isOpened():
            return None
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
        self.root.title("🧠 MagicBox: Mythic Memory Guard")
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

        self.status = tk.Label(root, text="🔍 Scanning for threats...", fg="lime", bg="#1e1e2f", font=("Consolas", 14))
        self.status.pack(pady=10)

        self.root.after(10, self.update_frame)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def update_frame(self):
        frame = self.camera.get_frame()
        if frame:
            img = ImageTk.PhotoImage(image=frame)
            self.canvas.configure(image=img)
            self.canvas.image = img
            self.status.config(text="✅ Live feed active")
        else:
            self.status.config(text="⚠️ Frame error: No valid image")
        self.root.after(30, self.update_frame)

    def on_close(self):
        if hasattr(self, 'camera'):
            self.camera.release()
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxApp(root)
    root.mainloop()

