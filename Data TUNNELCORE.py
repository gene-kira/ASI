# 🔧 TUNNELCORE: MagicBox Edition
# Mythic ASI GUI with auto-loader, passive tunneling, and cinematic feedback

import sys
import subprocess

# 🧙 Autoloader for required libraries
def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

# Auto-load essential libraries
for lib in ["tkinter", "random", "time"]:
    autoload(lib)

import tkinter as tk
from tkinter import ttk
import random
import time

# 🎨 GUI Theme Settings
BG_COLOR = "#0b0c10"
RING_COLOR = "#45a29e"
TEXT_COLOR = "#c5c6c7"
BTN_COLOR = "#1f2833"
ACTIVE_COLOR = "#66fcf1"

# 🌀 Ring Class: Represents a data tunnel
class DataRing:
    def __init__(self, canvas, x, y, radius, label):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.label = label
        self.ring = None
        self.text = None
        self.active = False

    def draw(self):
        color = ACTIVE_COLOR if self.active else RING_COLOR
        self.ring = self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            outline=color, width=3
        )
        self.text = self.canvas.create_text(
            self.x, self.y, text=self.label,
            fill=TEXT_COLOR, font=("Helvetica", 10, "bold")
        )

    def pulse(self):
        self.active = True
        self.canvas.itemconfig(self.ring, outline=ACTIVE_COLOR)
        self.canvas.after(500, self.deactivate)

    def deactivate(self):
        self.active = False
        self.canvas.itemconfig(self.ring, outline=RING_COLOR)

# 🧠 Main GUI Class
class TunnelCoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TUNNELCORE: MagicBox Edition")
        self.root.configure(bg=BG_COLOR)
        self.canvas = tk.Canvas(root, width=600, height=400, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=20)

        self.rings = []
        self.create_rings()

        self.activate_btn = tk.Button(
            root, text="Activate TUNNELCORE", command=self.activate,
            bg=BTN_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"), padx=20, pady=10
        )
        self.activate_btn.pack(pady=10)

        self.status_label = tk.Label(
            root, text="Status: Idle", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 10)
        )
        self.status_label.pack()

    def create_rings(self):
        positions = [
            (150, 100), (300, 100), (450, 100),
            (150, 200), (300, 200), (450, 200),
            (150, 300), (300, 300), (450, 300),
            (300, 380)
        ]
        labels = [
            "Shortcut", "Bot Revive", "Enemy Ping", "GUI Pulse", "Privacy Shield",
            "Mod Trigger", "Stress Signal", "Game Ingest", "Memory Echo", "Swarm Sync"
        ]
        for (x, y), label in zip(positions, labels):
            ring = DataRing(self.canvas, x, y, 30, label)
            ring.draw()
            self.rings.append(ring)

    def activate(self):
        self.status_label.config(text="Status: Tunneling...")
        for ring in self.rings:
            ring.pulse()
        self.root.after(1500, lambda: self.status_label.config(text="Status: Idle"))

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TunnelCoreGUI(root)
    root.mainloop()

