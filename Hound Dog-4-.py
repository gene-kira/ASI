import os
import sys
import subprocess
import threading
import tkinter as tk
from tkinter import ttk
import time
import json
import random

# 🧙 Auto-loader for required libraries
def autoload_libraries():
    required = ['psutil', 'pyttsx3']
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libraries()
import psutil, pyttsx3

# 🧠 Voice Engine Setup
voice_engine = pyttsx3.init()
voice_engine.setProperty('rate', 150)
voice_engine.setProperty('volume', 1.0)

def speak(text):
    voice_engine.say(text)
    voice_engine.runAndWait()

# 🧙 MagicBox Theme
MAGICBOX_COLORS = {
    "bg": "#1e1e2f",
    "fg": "#e0e0ff",
    "accent": "#6f00ff",
    "danger": "#ff3c3c",
    "safe": "#00ff99",
    "panel": "#2e2e3f"
}

# 🧠 ASI Memory Vault
MEMORY_FILE = "asi_memory_vault.json"
if not os.path.exists(MEMORY_FILE):
    with open(MEMORY_FILE, "w") as f:
        json.dump({"threats": []}, f)

def log_threat_to_memory(threat):
    with open(MEMORY_FILE, "r+") as f:
        data = json.load(f)
        data["threats"].append(threat)
        f.seek(0)
        json.dump(data, f, indent=2)

# 🧠 Main GUI Class
class MagicBoxSentinel(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 MagicBox Sentinel — No-Fear Edition")
        self.geometry("1200x800")
        self.configure(bg=MAGICBOX_COLORS["bg"])
        self.trust_threshold = 3
        self.glyphs = []
        self.create_tabs()
        self.create_status_pulse()
        self.start_real_time_listener()

    def create_tabs(self):
        notebook = ttk.Notebook(self)
        notebook.pack(expand=True, fill='both')

        self.watchtower_tab = ttk.Frame(notebook)
        self.ip_tracker_tab = ttk.Frame(notebook)
        self.threat_tab = ttk.Frame(notebook)
        self.voice_tab = ttk.Frame(notebook)
        self.config_tab = ttk.Frame(notebook)
        self.mutation_tab = ttk.Frame(notebook)
        self.glyph_tab = ttk.Frame(notebook)

        notebook.add(self.watchtower_tab, text="🕵️ Process Watchtower")
        notebook.add(self.ip_tracker_tab, text="🌐 Foreign IP Tracker")
        notebook.add(self.threat_tab, text="🔥 Threat Response")
        notebook.add(self.voice_tab, text="🗣️ Voice Feedback")
        notebook.add(self.config_tab, text="⚙️ Config Panel")
        notebook.add(self.mutation_tab, text="🧬 Mutation Trails")
        notebook.add(self.glyph_tab, text="🧠 GlyphCanvas")

        self.build_watchtower()
        self.build_ip_tracker()
        self.build_threat_response()
        self.build_voice_panel()
        self.build_config_panel()
        self.build_mutation_trails()
        self.build_glyph_canvas()

    def create_status_pulse(self):
        self.status_label = tk.Label(self, text="🟢 Sentinel Active", bg=MAGICBOX_COLORS["bg"], fg=MAGICBOX_COLORS["safe"], font=("Helvetica", 12))
        self.status_label.pack(side=tk.BOTTOM, fill=tk.X)

    def pulse_status(self):
        while True:
            now = time.strftime("%H:%M:%S")
            self.status_label.config(text=f"🟢 Sentinel Active — Last scan: {now}", fg=MAGICBOX_COLORS["safe"])
            time.sleep(5)

    def build_watchtower(self):
        label = tk.Label(self.watchtower_tab, text="Live Process Scan", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
        label.pack(fill=tk.X)
        self.process_output = tk.Text(self.watchtower_tab, bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Courier", 12))
        self.process_output.pack(expand=True, fill=tk.BOTH)

    def build_ip_tracker(self):
        label = tk.Label(self.ip_tracker_tab, text="Foreign IP Tracker", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
        label.pack(fill=tk.X)
        self.ip_output = tk.Text(self.ip_tracker_tab, bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Courier", 12))
        self.ip_output.pack(expand=True, fill=tk.BOTH)

    def build_threat_response(self):
        label = tk.Label(self.threat_tab, text="Threat Response Console", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
        label.pack(fill=tk.X)
        self.threat_output = tk.Text(self.threat_tab, bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Courier", 12))
        self.threat_output.pack(expand=True, fill=tk.BOTH)

    def build_voice_panel(self):
        label = tk.Label(self.voice_tab, text="Voice Feedback Settings", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
        label.pack(fill=tk.X)
        test_btn = ttk.Button(self.voice_tab, text="Test Voice", command=lambda: speak("Voice system online. Ready to defend."))
        test_btn.pack(pady=10)

    def build_config_panel(self):
        label = tk.Label(self.config_tab, text="Trust Rules & Kill Thresholds", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
        label.pack(fill=tk.X)
        slider = ttk.Scale(self.config_tab, from_=1, to=10, orient="horizontal", command=self.update_threshold)
        slider.set(self.trust_threshold)
        slider.pack(pady=20)
        self.threshold_label = tk.Label(self.config_tab, text=f"Kill Threshold: {self.trust_threshold}", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"])
        self.threshold_label.pack()

    def update_threshold(self, val):
        self.trust_threshold = int(float(val))
        self.threshold_label.config(text=f"Kill Threshold: {self.trust_threshold}")

    def build_mutation_trails(self):
        label = tk.Label(self.mutation_tab, text="Mutation Trail Logs", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
        label.pack(fill=tk.X)
        self.mutation_output = tk.Text(self.mutation_tab, bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["accent"], font=("Courier", 12))
        self.mutation_output.pack(expand=True, fill=tk.BOTH)

    def build_glyph_canvas(self):
        self.canvas = tk.Canvas(self.glyph_tab, bg=MAGICBOX_COLORS["bg"])
        self.canvas.pack(expand=True, fill=tk.BOTH)
        self.animate_glyphs()

    def animate_glyphs(self):
        self.canvas.delete("all")
        for glyph in self.glyphs:
            x, y, r, color = glyph
            self.canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
        self.after(100, self.animate_glyphs)

    def spawn_glyph(self):
        x = random.randint(50, 1150)
        y = random.randint(50, 750)
        r = random.randint(5, 20)
        color = random.choice([MAGICBOX_COLORS["accent"], MAGICBOX_COLORS["danger"], MAGICBOX_COLORS["safe"]])
        self.glyphs.append((x, y, r, color))
        if len(self.glyphs) > 100:
            self.glyphs.pop(0)

    def start_real_time_listener(self):
        threading.Thread(target=self.real_time_monitor, daemon=True).start()
        threading.Thread(target=self.pulse_status, daemon=True).start()

    def real_time_monitor(self):
        known_connections = set()
        while True:
            for proc in psutil.process_iter(['pid', 'name', 'connections']):
                try:
                    name = proc.info['name']
                    pid = proc.info['pid']
                    conns = proc.info['connections']
                    score = 0
                    for conn in conns:
                        if conn.raddr and hasattr(conn.raddr, 'ip'):
                            ip = conn.raddr.ip
                            key = f"{name}-{pid}-{ip}"
                            if key not in known_connections:
                                known_connections.add(key)
                                score += 1
                                msg = f"⚠️ {name} (PID {pid}) connected to {ip}\n"
                                self.process_output.insert(tk.END, msg)
                                self.ip_output.insert(tk.END, msg)
                                self.threat_output.insert(tk.END, f"🔥 Threat logged: {msg}")
                                self.mutation_output.insert(tk.END, f"🧬 Mutation: {name} reached {ip}\n")
                                speak(f"Suspicious connection detected from {name} to {ip}.")
                                log_threat_to_memory({"name": name, "pid": pid, "ip": ip, "timestamp": time.time()})
                                self.spawn_glyph()
                    if score >= self.trust_threshold:
                        self.terminate_process(pid, name)
                except Exception as e:
                    print(f"[Monitor Error] {e}")
            time.sleep(5)


if __name__ == "__main__":
    app = MagicBoxSentinel()
    app.mainloop()


