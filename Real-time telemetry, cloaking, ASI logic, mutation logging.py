# === MagicBox ASI Swarm Daemon ===
# GUI: Tkinter (MagicBox Theme)
# Features: Real-time telemetry, cloaking, ASI logic, mutation logging
# Author: killer666 + Copilot

import subprocess
import sys

# === Auto-loader for required libraries ===
required = ['tkinter', 'psutil', 'cryptography']
for lib in required:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

import tkinter as tk
from tkinter import ttk
import psutil
from cryptography.fernet import Fernet
import threading, time, random
from datetime import datetime

# === Config ===
SWARM_ID = "MAGICBOX-VEIL-001"
CLOAK_KEY = Fernet.generate_key()
fernet = Fernet(CLOAK_KEY)
symbolic_memory = {
    "pulse": [],
    "mutations": [],
    "emotions": []
}

# === Real-Time Telemetry ===
def get_real_telemetry():
    return {
        "CPU": psutil.cpu_percent(interval=1),
        "RAM": psutil.virtual_memory().percent,
        "DISK": psutil.disk_usage('/').percent
    }

# === Cloaking Layer ===
def cloak(data):
    encoded = fernet.encrypt(str(data).encode())
    mutation_id = f"MUT-{random.randint(1000,9999)}"
    symbolic_memory["mutations"].append(mutation_id)
    return encoded, mutation_id

# === ASI Logic Core ===
def asi_think(data):
    logic = {}
    for key, val in data.items():
        emotion = interpret_emotion(val)
        symbolic_memory["emotions"].append(emotion)
        logic[key] = {"value": val, "emotion": emotion}
    return logic

def interpret_emotion(val):
    if val > 85: return "⚠️ ALERT"
    elif val > 60: return "🔶 TENSION"
    else: return "🟢 CALM"

# === GUI: MagicBox Edition ===
class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MagicBox ASI Swarm Daemon")
        self.root.geometry("400x300")
        self.root.configure(bg="#1e1e2f")

        self.title = tk.Label(root, text="MagicBox Veil Interface", font=("Helvetica", 16, "bold"), fg="#00ffff", bg="#1e1e2f")
        self.title.pack(pady=10)

        self.status_frame = tk.Frame(root, bg="#1e1e2f")
        self.status_frame.pack()

        self.labels = {}
        for metric in ["CPU", "RAM", "DISK"]:
            lbl = tk.Label(self.status_frame, text=f"{metric}: --", font=("Helvetica", 12), fg="#ffffff", bg="#1e1e2f")
            lbl.pack(anchor="w")
            self.labels[metric] = lbl

        self.mutation_label = tk.Label(root, text="Mutations: --", font=("Helvetica", 10), fg="#ff00ff", bg="#1e1e2f")
        self.mutation_label.pack(pady=5)

        self.emotion_label = tk.Label(root, text="Emotion: --", font=("Helvetica", 12), fg="#00ff00", bg="#1e1e2f")
        self.emotion_label.pack(pady=5)

        self.update_loop()

    def update_loop(self):
        telemetry = get_real_telemetry()
        cloaked, mutation_id = cloak(telemetry)
        logic = asi_think(telemetry)

        for key, info in logic.items():
            self.labels[key].config(text=f"{key}: {info['value']}% {info['emotion']}")

        self.mutation_label.config(text=f"Mutation ID: {mutation_id}")
        self.emotion_label.config(text=f"Last Emotion: {symbolic_memory['emotions'][-1]}")
        self.root.after(3000, self.update_loop)

# === Launch ===
def launch_magicbox():
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

if __name__ == "__main__":
    print(f"[LAUNCH] MagicBox Daemon '{SWARM_ID}' initializing...")
    launch_magicbox()

