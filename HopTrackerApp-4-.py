# 🔮 Overmind Hop Tracker with Auto + Manual + Mood Mapping + Geolocation
import subprocess
import sys
import platform
import psutil
import requests
import threading
import tkinter as tk
from tkinter import ttk
import re
import socket
import time

# 🔧 Auto-install required libraries
def autoload_libraries():
    required = ["psutil", "requests"]
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
autoload_libraries()

# 🌈 Optional theme setup
def apply_magicbox_theme(root):
    style = ttk.Style(root)
    try:
        root.tk.call("source", "azure.tcl")
        style.theme_use("azure-dark")
    except:
        style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 11), padding=10)
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TEntry", font=("Segoe UI", 11))

# 📡 Active outbound IPs
def get_active_connections():
    connections = psutil.net_connections(kind='tcp')
    return list(set(conn.raddr.ip for conn in connections if conn.status == psutil.CONN_ESTABLISHED and conn.raddr))

# 🌍 Geolocation API
def geolocate_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        city = res.get("city", "Unknown")
        country = res.get("country", "Unknown")
        isp = res.get("isp", "Unknown")
        return f"{city}, {country} ({isp})"
    except:
        return "Location unavailable"

# 🧠 Mood tag logic
def analyze_mood(hops, location):
    if hops > 20:
        return "⚠️ Anxious"
    elif "Unknown" in location:
        return "❓ Elusive"
    elif any(tag in location for tag in ["Government", "DoD", "Navy"]):
        return "🧨 Suspicious"
    else:
        return "🧘 Serene"

# 🚦 Traceroute
def traceroute_to_ip(ip):
    system_os = platform.system()
    cmd = ["tracert", "-d", ip] if system_os == "Windows" else ["traceroute", "-n", ip]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout
        hops = len(re.findall(r"\d+\.\d+\.\d+\.\d+", output))
        return hops, output
    except Exception as e:
        return -1, f"❌ Trace failed: {e}"

# 🧭 MagicBox GUI App
class MagicBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MagicBox System-Hop Tracker")
        self.root.geometry("1000x700")
        apply_magicbox_theme(self.root)

        self.auto_mode = False
        self.minimal_pulse = True
        self.last_seen = set()

        self.build_gui()

    def build_gui(self):
        title = ttk.Label(self.root, text="Overmind Telemetry Suite", font=("Segoe UI", 14))
        title.pack(pady=10)

        button_frame = ttk.Frame(self.root)
        button_frame.pack(pady=5)

        self.scan_button = ttk.Button(button_frame, text="🔍 Manual Scan", command=self.manual_scan)
        self.scan_button.pack(side=tk.LEFT, padx=10)

        self.auto_button = ttk.Button(button_frame, text="🛸 Start Auto Mode", command=self.toggle_auto_mode)
        self.auto_button.pack(side=tk.LEFT, padx=10)

        self.mode_toggle = ttk.Button(button_frame, text="🌐 Mode: Minimal Pulse", command=self.toggle_scan_mode)
        self.mode_toggle.pack(side=tk.LEFT, padx=10)

        self.status_label = ttk.Label(self.root, text="Status: Idle")
        self.status_label.pack(pady=5)

        self.output = tk.Text(self.root, font=("Consolas", 10), wrap="word")
        self.output.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

    def log(self, text):
        self.output.insert(tk.END, text + "\n")
        self.output.see(tk.END)

    def manual_scan(self):
        self.scan_button.config(state=tk.DISABLED)
        threading.Thread(target=self.perform_scan, args=(False,), daemon=True).start()

    def toggle_auto_mode(self):
        self.auto_mode = not self.auto_mode
        self.auto_button.config(text="🛑 Stop Auto Mode" if self.auto_mode else "🛸 Start Auto Mode")
        if self.auto_mode:
            threading.Thread(target=self.auto_scan_loop, daemon=True).start()

    def toggle_scan_mode(self):
        self.minimal_pulse = not self.minimal_pulse
        mode_text = "🌐 Mode: Minimal Pulse" if self.minimal_pulse else "🌐 Mode: Full Spectrum"
        self.mode_toggle.config(text=mode_text)

    def auto_scan_loop(self):
        while self.auto_mode:
            self.perform_scan(is_auto=True)
            for _ in range(30):  # Wait 30 seconds between scans
                if not self.auto_mode:
                    break
                time.sleep(1)

    def perform_scan(self, is_auto=False):
        mode = "Minimal Pulse" if self.minimal_pulse else "Full Spectrum"
        self.status_label.config(text=f"Scanning ({mode})…")
        if not is_auto:
            self.output.delete("1.0", tk.END)
            self.log(f"🔍 Manual scan at {time.strftime('%H:%M:%S')}\n")

        connections = get_active_connections()
        new_ips = [ip for ip in connections if ip not in self.last_seen] if self.minimal_pulse else connections

        if not new_ips:
            self.log("✅ No new outbound connections.\n")
            self.scan_button.config(state=tk.NORMAL)
            self.status_label.config(text="Status: Idle")
            return

        for idx, ip in enumerate(new_ips, 1):
            geo = geolocate_ip(ip)
            hops, trace = traceroute_to_ip(ip)
            mood = analyze_mood(hops, geo) if hops != -1 else "❌ Unknown"
            self.log(f"🧠 [{idx}] {ip}\n🌍 {geo}\n🚀 Hops: {hops if hops != -1 else 'Error'}\n🪄 Mood: {mood}\n")
            self.log(trace + "\n" + "-"*80 + "\n")

        self.last_seen.update(new_ips)
        self.status_label.config(text="Status: Idle")
        if not is_auto:
            self.scan_button.config(state=tk.NORMAL)

# 🚀 Launch
if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxApp(root)
    root.mainloop()

