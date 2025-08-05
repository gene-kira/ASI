import sys
import subprocess
import importlib
import time
import json
import os

# 🛠 Required libraries auto-loader
required_libs = ['networkx', 'psutil']
for lib in required_libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# 🎬 Imports
import tkinter as tk
from tkinter import filedialog, messagebox
import platform
import psutil
import networkx as nx
import subprocess
from concurrent.futures import ThreadPoolExecutor, as_completed

CACHE_PATH = "hops_cache.json"

# 🧠 ASI Logger
class ASILogger:
    def __init__(self):
        self.logs = []
        self.mood = "neutral"

    def log(self, msg):
        self.logs.append(msg)
        print("[ASI]", msg)

    def escalate_mood(self, new_mood):
        self.mood = new_mood
        self.log(f"Overmind mood → {new_mood}")

    def get_logs(self):
        return "\n".join(self.logs)

# 🧪 Hopper core logic
class MagicBoxHopper:
    def __init__(self, asi):
        self.asi = asi
        self.cache = self.load_cache()
        self.G = nx.Graph()

    def load_cache(self):
        if os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, 'r') as f:
                    return json.load(f)
            except Exception as e:
                self.asi.log(f"Cache load error: {e}")
        return {}

    def save_cache(self):
        try:
            with open(CACHE_PATH, 'w') as f:
                json.dump(self.cache, f, indent=2)
            self.asi.log("Cache saved.")
        except Exception as e:
            self.asi.log(f"Cache save error: {e}")

    def load_graph(self, path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    src, dst, weight = line.strip().split(',')
                    self.G.add_edge(src, dst, weight=int(weight))
            self.asi.log(f"Graph loaded from {path}")
        except Exception as e:
            self.asi.log(f"Graph error: {e}")

    def shortest_hop(self, start, end):
        try:
            path = nx.shortest_path(self.G, source=start, target=end, weight='weight')
            self.asi.log(f"{start} → {end}: {path}")
            return path
        except Exception as e:
            self.asi.log(f"Hop fail: {e}")
            return []

    def trace_hops(self, ip):
        try:
            cmd = ['tracert', '-d', ip] if platform.system() == 'Windows' else ['traceroute', ip]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            lines = [line for line in result.stdout.splitlines() if line.strip() and line[0].isdigit()]
            return len(lines)
        except Exception as e:
            self.asi.log(f"Trace failed for {ip}: {e}")
            return -1

    def reroute_ip(self, ip):
        try:
            if platform.system() == 'Windows':
                cmd = ['route', 'ADD', ip, 'MASK', '255.255.255.255', '192.168.1.1']
            else:
                cmd = ['ip', 'route', 'add', ip, 'via', '192.168.1.1']
            subprocess.run(cmd, check=True)
            self.asi.log(f"Route override: {ip} → 192.168.1.1")
        except Exception as e:
            self.asi.log(f"Override error: {e}")

    def evaluate_connection(self, ip):
        if ip in self.cache and self.cache[ip]['status'] == 'stable':
            return ip, self.cache[ip]['info']

        hops = self.trace_hops(ip)
        mood = ""
        status = "stable"

        if hops < 5:
            mood = "green"
        elif hops <= 10:
            mood = "orange"
            status = "unstable"
        else:
            mood = "red"
            status = "hostile"
            self.reroute_ip(ip)

        info = f"{hops} hops [{mood}]"
        self.cache[ip] = {'hops': hops, 'mood': mood, 'status': status, 'info': info}
        self.asi.escalate_mood(mood)
        self.asi.log(f"{ip}: {info}")
        return ip, info

    def scan_outbound(self):
        outbound = [c for c in psutil.net_connections(kind='inet') if c.status == 'ESTABLISHED' and c.raddr]
        results = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(self.evaluate_connection, c.raddr.ip): c.raddr.ip for c in outbound}
            for future in as_completed(futures):
                ip, info = future.result()
                results[ip] = info
        self.save_cache()
        return results

    def auto_loop(self, interval=600):  # default: every 10 minutes
        while True:
            self.asi.log("Starting optimization loop...")
            self.scan_outbound()
            self.asi.log(f"Cycle complete. Sleeping for {interval} seconds...")
            time.sleep(interval)

# 🎛 GUI interface
class MagicBoxGUI:
    def __init__(self, hopper):
        self.hopper = hopper
        self.root = tk.Tk()
        self.root.title("MagicBox Hopper 🌌 Persistent Overmind")
        self.root.geometry("560x460")
        self.root.configure(bg="#1a1d2d")
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Start Node:", bg="#1a1d2d", fg="white").pack()
        self.start_entry = tk.Entry(self.root)
        self.start_entry.pack()

        tk.Label(self.root, text="End Node:", bg="#1a1d2d", fg="white").pack()
        self.end_entry = tk.Entry(self.root)
        self.end_entry.pack()

        tk.Button(self.root, text="Load Graph 📁", command=self.load_graph).pack(pady=5)
        tk.Button(self.root, text="Find Shortest Hop ↯", command=self.find_hop).pack(pady=5)
        tk.Button(self.root, text="Scan & Optimize 🚀", command=self.scan_optimize).pack(pady=5)
        tk.Button(self.root, text="Show Logs 📜", command=self.show_logs).pack(pady=5)
        tk.Button(self.root, text="Start Auto Optimization 🔁", command=self.start_loop).pack(pady=5)

    def load_graph(self):
        path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv")])
        if path:
            self.hopper.load_graph(path)

    def find_hop(self):
        start = self.start_entry.get()
        end = self.end_entry.get()
        path = self.hopper.shortest_hop(start, end)
        messagebox.showinfo("Shortest Hop", str(path))

    def scan_optimize(self):
        results = self.hopper.scan_outbound()
        display = "\n".join([f"{ip}: {info}" for ip, info in results.items()])
        messagebox.showinfo("System Hop Scan", display or "No outbound connections found.")

    def show_logs(self):
        logs = self.hopper.asi.get_logs()
        messagebox.showinfo("ASI Tracker Logs", logs)

    def start_loop(self):
        import threading
        threading.Thread(target=self.hopper.auto_loop, daemon=True).start()
        messagebox.showinfo("Auto Optimization", "Loop started. Will run every 10 mins.")

    def run(self):
        self.root.mainloop()

# 🚀 Launch
if __name__ == "__main__":
    asi = ASILogger()
    hopper = MagicBoxHopper(asi)
    gui = MagicBoxGUI(hopper)
    gui.run()

