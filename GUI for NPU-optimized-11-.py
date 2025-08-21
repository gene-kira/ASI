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
import pyttsx3
from bs4 import BeautifulSoup

# --- WebPageScanner ---
class WebPageScanner:
    def __init__(self, url):
        self.url = url
        self.html = None
        self.soup = None

    def fetch(self):
        try:
            response = requests.get(self.url, timeout=5)
            self.html = response.text
            self.soup = BeautifulSoup(self.html, 'html.parser')
            return True
        except Exception as e:
            print("Web fetch error:", e)
            return False

# --- ProblemDetector ---
class ProblemDetector:
    def __init__(self, soup):
        self.soup = soup

    def analyze(self):
        problems = []
        if not self.soup.title or not self.soup.title.string:
            problems.append("Missing page title.")
        if not self.soup.find_all('img', alt=True):
            problems.append("Images missing alt text.")
        if len(self.soup.find_all('a')) == 0:
            problems.append("No hyperlinks found.")
        return problems

# --- VoiceAlert ---
class VoiceAlert:
    def __init__(self):
        self.engine = pyttsx3.init()

    def speak(self, message):
        self.engine.say(message)
        self.engine.runAndWait()

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
    def render(draw, box, score):
        x, y, w, h = box
        color = "red" if score > 0.7 else "orange" if score > 0.4 else "yellow"
        glyph = "🎯"
        draw.rectangle([x, y, x+w, y+h], outline=color, width=2)
        draw.text((x, y-20), f"{glyph} {int(score*100)}%", fill=color)

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
        self.root.title("🧠 MagicBox v7.0: Web-Aware Mythic Sentinel")
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
        self.vault = VaultSyncEngine(node_id="node-007")
        self.voice = VoiceAlert()

        # Web analysis trigger
        self.scan_webpage("https://example.com")

        self.root.after(10, self.update_frame)
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)

    def scan_webpage(self, url):
        scanner = WebPageScanner(url)
        if scanner.fetch():
            detector = ProblemDetector(scanner.soup)
            issues = detector.analyze()
            if issues:
                for problem in issues:
                    print("⚠️", problem)
                    self.voice.speak(f"Warning: {problem}")
            else:
                self.voice.speak("Webpage scan complete. No problems detected.")

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
                    self.vault.sync(f"target-{i}", score, center)

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

