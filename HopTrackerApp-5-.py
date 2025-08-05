# 🔮 Overmind Hop Tracker GUI: Manual + Auto + Mood + Geolocation + Live Legend

import subprocess
import sys
import platform
import psutil
import requests
import threading
import tkinter as tk
from tkinter import ttk
import re
import time

# 🛠 Auto-install required libraries
def autoload_libraries():
    required = ["psutil", "requests"]
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
autoload_libraries()

# 🌈 GUI Theme Setup
def apply_magicbox_theme(root):
    style = ttk.Style(root)
    try:
        root.tk.call("source", "azure.tcl")
        style.theme_use("azure-dark")
    except:
        style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 11), padding=8)
    style.configure("TLabel", font=("Segoe UI", 11))
    style.configure("TEntry", font=("Segoe UI", 11))

# 📡 Get outbound IPs
def get_active_connections():
    conns = psutil.net_connections(kind='tcp')
    return list(set(conn.raddr.ip for conn in conns if conn.status == psutil.CONN_ESTABLISHED and conn.raddr))

# 🌍 IP Geolocation
def geolocate_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}", timeout=5).json()
        city = res.get("city", "Unknown")
        country = res.get("country", "Unknown")
        isp = res.get("isp", "Unknown")
        return f"{city}, {country}", country, isp
    except:
        return "Location unavailable", "Unknown", "Unknown"

# 🎭 Mood analysis
def analyze_mood(hops, country, local_country="United States"):
    if hops > 20:
        return "⚠️ Anxious"
    elif country != local_country and country != "Unknown":
        return "🧨 Suspicious"
    elif country == "Unknown":
        return "❓ Elusive"
    else:
        return "🧘 Serene"

# 🎨 Color classification
def classify_color(country, local_country="United States"):
    if country == "Unknown":
        return "gray"
    elif country == local_country:
        return "black"
    elif country not in ["United States"]:
        return "red"
    else:
        return "blue"

# 🚀 Traceroute function
def traceroute_to_ip(ip):
    cmd = ["tracert", "-d", ip] if platform.system() == "Windows" else ["traceroute", "-n", ip]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout
        hops = len(re.findall(r"\d+\.\d+\.\d+\.\d+", output))
        return hops, output
    except Exception as e:
        return -1, f"❌ Trace failed: {e}"

# 🧭 Main GUI Class
class MagicBoxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MagicBox System-Hop Tracker")
        self.root.geometry("1200x700")
        apply_magicbox_theme(self.root)

        self.auto_mode = False
        self.minimal_mode = True
        self.last_seen = set()

        self.build_gui()

    def build_gui(self):
        top_frame = ttk.Frame(self.root)
        top_frame.pack(pady=10)

        ttk.Button(top_frame, text="🔍 Manual Scan", command=self.manual_scan).pack(side=tk.LEFT, padx=5)
        ttk.Button(top_frame, text="🛸 Toggle Auto Mode", command=self.toggle_auto).pack(side=tk.LEFT, padx=5)
        self.mode_toggle = ttk.Button(top_frame, text="Mode: Minimal Pulse", command=self.toggle_mode)
        self.mode_toggle.pack(side=tk.LEFT, padx=5)

        self.status_label = ttk.Label(self.root, text="Status: Idle")
        self.status_label.pack(pady=5)

        body_frame = ttk.Frame(self.root)
        body_frame.pack(expand=True, fill=tk.BOTH, padx=10)

        self.output_text = tk.Text(body_frame, font=("Consolas", 10), wrap="word")
        self.output_text.pack(side=tk.LEFT, expand=True, fill=tk.BOTH)

        self.legend_frame = ttk.Frame(body_frame, width=300)
        self.legend_frame.pack(side=tk.RIGHT, fill=tk.Y)
        ttk.Label(self.legend_frame, text="🧾 Hop Legend").pack(pady=5)
        self.legend_list = tk.Listbox(self.legend_frame, font=("Segoe UI", 10))
        self.legend_list.pack(expand=True, fill=tk.BOTH, padx=5)

    def toggle_mode(self):
        self.minimal_mode = not self.minimal_mode
        mode_text = "Mode: Minimal Pulse" if self.minimal_mode else "Mode: Full Spectrum"
        self.mode_toggle.config(text=mode_text)

    def toggle_auto(self):
        self.auto_mode = not self.auto_mode
        if self.auto_mode:
            threading.Thread(target=self.auto_loop, daemon=True).start()

    def auto_loop(self):
        while self.auto_mode:
            self.perform_scan(is_auto=True)
            for _ in range(30):
                if not self.auto_mode:
                    break
                time.sleep(1)

    def manual_scan(self):
        threading.Thread(target=self.perform_scan, args=(False,), daemon=True).start()

    def perform_scan(self, is_auto=False):
        self.status_label.config(text="Scanning…")
        if not is_auto:
            self.output_text.delete("1.0", tk.END)
            self.legend_list.delete(0, tk.END)

        ips = get_active_connections()
        new_ips = [ip for ip in ips if ip not in self.last_seen] if self.minimal_mode else ips

        if not new_ips:
            self.output_text.insert(tk.END, "✅ No new connections.\n")
            self.status_label.config(text="Idle")
            return

        for ip in new_ips:
            location, country, isp = geolocate_ip(ip)
            hops, trace = traceroute_to_ip(ip)
            mood = analyze_mood(hops, country)
            color = classify_color(country)

            self.output_text.insert(tk.END, f"🧠 IP: {ip}\n", color)
            self.output_text.insert(tk.END, f"🌍 Location: {location} ({isp})\n", color)
            self.output_text.insert(tk.END, f"🚀 Hops: {hops if hops != -1 else 'Error'}\n", color)
            self.output_text.insert(tk.END, f"🪄 Mood: {mood}\n", color)
            self.output_text.insert(tk.END, trace + "\n" + "-"*70 + "\n", color)

            self.output_text.tag_config("red", foreground="red")
            self.output_text.tag_config("black", foreground="black")
            self.output_text.tag_config("blue", foreground="blue")
            self.output_text.tag_config("gray", foreground="gray")

            stamp = time.strftime("%H:%M:%S")
            self.legend_list.insert(tk.END, f"[{stamp}] {ip} - {mood}")
            self.legend_list.itemconfig(tk.END, foreground=color)

        self.last_seen.update(new_ips)
        self.status_label.config(text="Idle")

# 🚀 Launch App
if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxApp(root)
    root.mainloop()

