# 📦 Auto-loader
import subprocess, sys
def ensure_libraries():
    for lib in ['psutil', 'requests', 'pyttsx3', 'pandas', 'pycaw']:
        try: __import__(lib)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
ensure_libraries()

# 🧠 Imports
import tkinter as tk
from tkinter import ttk, messagebox, Toplevel, Text
import psutil, requests, pyttsx3, pandas as pd, subprocess
from datetime import datetime
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from comtypes import CLSCTX_ALL
from ctypes import cast, POINTER
from concurrent.futures import ThreadPoolExecutor

# 🖼️ Splash Screen
def show_splash():
    splash = tk.Toplevel()
    splash.title("Launching MagicBox ASI...")
    splash.geometry("400x200")
    ttk.Label(splash, text="🧙‍♂️ MagicBox ASI Super Agent", font=("Segoe UI", 16)).pack(pady=30)
    ttk.Label(splash, text="Initializing modules... 🔄", font=("Segoe UI", 12)).pack()
    splash.after(3000, splash.destroy)
    splash.grab_set()

# 🌐 GeoIP Tracker
class GeoIPTracker:
    def __init__(self, token='your_token_here'):
        self.url = 'https://ipinfo.io/{ip}/json?token=' + token
    def lookup(self, ip):
        try:
            response = requests.get(self.url.format(ip=ip), timeout=3)
            data = response.json()
            return f"{data.get('city')}, {data.get('region')}, {data.get('country')}"
        except:
            return "GeoIP lookup failed"

# 💣 Threat Scoring
class ThreatScorer:
    def score(self, location, ip):
        score = 0
        risky = ["CN", "RU", "IR", "KP", "SY"]
        if any(code in location for code in risky): score += 50
        if "TOR" in location or "Proxy" in location: score += 30
        try: score += int(ip.split(".")[0]) // 2
        except: pass
        return min(score, 100)

# 🛡️ Auto-Responder
class AutoResponder:
    def block_ip(self, ip):
        try:
            subprocess.run(f'netsh advfirewall firewall add rule name="Block {ip}" dir=in action=block remoteip={ip}', shell=True)
            return True
        except: return False

# 📓 Event Logger
class EventLogger:
    def __init__(self): self.file = "magicbox.log"
    def log(self, msg):
        with open(self.file, "a", encoding="utf-8") as f:
            f.write(f"[{datetime.now()}] {msg}\n")

# 🔍 Connection Scanner
class SystemScanner:
    def get_connections(self):
        flagged = []
        for conn in psutil.net_connections(kind='inet'):
            if conn.raddr:
                ip = conn.raddr.ip
                if not ip.startswith(('127.', '10.', '192.')): flagged.append(ip)
        return list(set(flagged))

# 📊 System Stats
class LiveStats:
    def get_stats(self):
        cpu = psutil.cpu_percent(interval=1)
        ram = psutil.virtual_memory().percent
        net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        return cpu, ram, net // 1024

# 🔊 Voice Feedback
class VoiceEngine:
    def __init__(self):
        self.engine = pyttsx3.init()
        self.engine.setProperty('rate', 160)
    def speak(self, text):
        self.engine.say(text)
        self.engine.runAndWait()

# 🔈 Volume Control
class VolumeController:
    def mute(self):
        devices = AudioUtilities.GetSpeakers()
        interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
        volume = cast(interface, POINTER(IAudioEndpointVolume))
        volume.SetMute(1, None)

# 🧙‍♂️ GUI Controller
class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧙‍♂️ MagicBox ASI Super Agent")
        self.root.geometry("600x400")
        self.geo = GeoIPTracker()
        self.score = ThreatScorer()
        self.responder = AutoResponder()
        self.logger = EventLogger()
        self.scanner = SystemScanner()
        self.stats = LiveStats()
        self.voice = VoiceEngine()
        self.volume = VolumeController()
        self.executor = ThreadPoolExecutor(max_workers=4)
        self.build_gui()
        self.update_stats()

    def build_gui(self):
        ttk.Label(self.root, text="MagicBox ASI Super Agent", font=("Segoe UI", 18)).pack(pady=10)
        self.status = ttk.Label(self.root, text="Status: Idle", font=("Segoe UI", 12))
        self.status.pack()
        self.output = Text(self.root, height=10, width=70)
        self.output.pack(pady=10)
        ttk.Button(self.root, text="Scan & Defend", command=self.scan_and_defend).pack(pady=5)
        ttk.Button(self.root, text="Mute System", command=self.volume.mute).pack(pady=5)

    def update_stats(self):
        cpu, ram, net = self.stats.get_stats()
        self.status.config(text=f"CPU: {cpu}% | RAM: {ram}% | Net: {net} KB")
        self.root.after(3000, self.update_stats)

    def scan_and_defend(self):
        self.output.delete("1.0", tk.END)
        self.voice.speak("Scanning active connections...")
        ips = self.scanner.get_connections()
        for ip in ips:
            self.executor.submit(self.process_ip, ip)

    def process_ip(self, ip):
        location = self.geo.lookup(ip)
        score = self.score.score(location, ip)
        action = "Blocked" if score > 50 and self.responder.block_ip(ip) else "Allowed"
        msg = f"{ip} | {location} | Threat Score: {score} → {action}"
        self.logger.log(msg)
        self.output.insert(tk.END, msg + "\n")
        if score > 80: self.voice.speak(f"High threat detected from {location}. IP blocked.")

# 🚀 Launch Sequence
if __name__ == "__main__":
    root = tk.Tk()
    show_splash()
    app = MagicBoxGUI(root)
    root.mainloop()

