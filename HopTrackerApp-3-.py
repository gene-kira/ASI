# 🧠 MagicBox Overmind Hop Tracker: Full GUI System
import subprocess
import sys
import platform
import psutil
import requests
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import re
import socket

# 🔧 Auto-install required libraries (psutil, requests)
def autoload_libraries():
    required = ["psutil", "requests"]
    for lib in required:
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libraries()

# 🌈 Optional: Apply GUI theme (fallback if theme file not present)
def apply_magicbox_theme(root):
    style = ttk.Style(root)
    try:
        root.tk.call("source", "azure.tcl")  # Make sure this file is in your directory
        style.theme_use("azure-dark")
    except:
        style.theme_use("clam")
    style.configure("TButton", font=("Segoe UI", 12), padding=10)
    style.configure("TLabel", font=("Segoe UI", 12))
    style.configure("TEntry", font=("Segoe UI", 12))

# 📡 Detect all active outbound IPs
def get_active_connections():
    connections = psutil.net_connections(kind='tcp')
    outbound_ips = set()
    for conn in connections:
        if conn.status == psutil.CONN_ESTABLISHED and conn.raddr:
            outbound_ips.add(conn.raddr.ip)
    return list(outbound_ips)

# 🌍 IP Geolocation via public API
def geolocate_ip(ip):
    try:
        res = requests.get(f"http://ip-api.com/json/{ip}").json()
        city = res.get("city", "Unknown")
        country = res.get("country", "Unknown")
        isp = res.get("isp", "Unknown")
        return f"{city}, {country} ({isp})"
    except:
        return "Location unavailable"

# 🧠 Mood / Emotion Tagging Logic
def analyze_mood(hop_count, geo_data):
    if hop_count > 20:
        return "⚠️ Anxious"
    elif "Unknown" in geo_data:
        return "❓ Elusive"
    elif "Government" in geo_data or "DoD" in geo_data or "Navy" in geo_data:
        return "🧨 Suspicious"
    else:
        return "🧘‍♂️ Serene"

# 🚦 Run traceroute to given IP
def traceroute_to_ip(ip):
    system_os = platform.system()
    cmd = ["tracert", "-d", ip] if system_os == "Windows" else ["traceroute", "-n", ip]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        output = result.stdout
        hops = len(re.findall(r"\d+\.\d+\.\d+\.\d+", output))
        return hops, output
    except Exception as e:
        return -1, f"❌ Error: {str(e)}"

# 🖼️ MagicBox GUI Class
class MagicBoxGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧙‍♂️ MagicBox System-Hop Tracker")
        self.root.geometry("1000x650")
        apply_magicbox_theme(self.root)
        self.build_gui()

    def build_gui(self):
        ttk.Label(self.root, text="System-Hop Surveillance", font=("Segoe UI", 14)).pack(pady=10)

        self.scan_button = ttk.Button(self.root, text="🔍 Scan & Trace", command=self.begin_scan)
        self.scan_button.pack(pady=10)

        self.output_box = tk.Text(self.root, font=("Consolas", 10), wrap="word")
        self.output_box.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

    def begin_scan(self):
        self.output_box.delete("1.0", tk.END)
        self.scan_button.config(state=tk.DISABLED)
        threading.Thread(target=self.scan_and_trace, daemon=True).start()

    def scan_and_trace(self):
        self.output_box.insert(tk.END, "🔎 Scanning outbound system connections...\n\n")
        connections = get_active_connections()

        if not connections:
            self.output_box.insert(tk.END, "⚠️ No outbound connections found.\n")
            self.scan_button.config(state=tk.NORMAL)
            return

        for idx, ip in enumerate(connections, start=1):
            self.output_box.insert(tk.END, f"🧠 [{idx}] Target IP: {ip}\n")
            geo_data = geolocate_ip(ip)
            hops, raw_trace = traceroute_to_ip(ip)
            mood = analyze_mood(hops, geo_data) if hops != -1 else "❌ Unknown"

            self.output_box.insert(tk.END, f"🌍 Location: {geo_data}\n")
            self.output_box.insert(tk.END, f"🚀 Hop Count: {hops if hops != -1 else 'Trace Error'}\n")
            self.output_box.insert(tk.END, f"🪄 Mood Tag: {mood}\n\n")
            self.output_box.insert(tk.END, raw_trace + "\n")
            self.output_box.insert(tk.END, "-" * 80 + "\n")

        self.output_box.insert(tk.END, "✅ Trace complete.\n")
        self.scan_button.config(state=tk.NORMAL)

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

