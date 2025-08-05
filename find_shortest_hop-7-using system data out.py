# === System Setup & Imports ===
import sys, os, json, time, subprocess, platform, importlib
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# === Auto-Install Dependencies ===
required_libs = ['psutil', 'networkx', 'pyttsx3', 'requests']
for lib in required_libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# === External Libraries ===
import networkx as nx
import psutil
import pyttsx3
import requests

# === Constants ===
CACHE_PATH = "hopper_override_cache.json"
GRAPH_PATH = "hopper_graph.csv"
VOICE_PERSONAS = {
    'sentinel': {'rate': 150, 'volume': 1.0},
    'muse':     {'rate': 130, 'volume': 0.9},
    'overseer': {'rate': 180, 'volume': 0.8}
}

# === Voice System ===
engine = pyttsx3.init()

def set_voice(persona):
    profile = VOICE_PERSONAS.get(persona, VOICE_PERSONAS['sentinel'])
    engine.setProperty('rate', profile['rate'])
    engine.setProperty('volume', profile['volume'])

def speak(text, persona='sentinel'):
    set_voice(persona)
    engine.say(text)
    engine.runAndWait()

# === ASI Logger ===
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

# === Hopper Guardian Intelligence ===
class OvermindGuardian:
    def __init__(self, asi):
        self.asi = asi
        self.cache = self.load_cache()
        self.G = nx.Graph()

    def load_cache(self):
        if os.path.exists(CACHE_PATH):
            try:
                with open(CACHE_PATH, 'r') as f:
                    return json.load(f)
            except:
                self.asi.log("Cache load error")
        return {}

    def save_cache(self):
        try:
            with open(CACHE_PATH, 'w') as f:
                json.dump(self.cache, f, indent=2)
        except:
            self.asi.log("Cache save error")

    def get_country(self, ip):
        try:
            return requests.get(f'https://ipinfo.io/{ip}/json').json().get('country', 'Unknown')
        except:
            return 'Unknown'

    def trace_hops(self, ip):
        try:
            cmd = ['tracert', '-d', ip] if platform.system() == 'Windows' else ['traceroute', ip]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=10)
            lines = [line for line in result.stdout.splitlines() if line.strip() and line[0].isdigit()]
            return len(lines)
        except Exception as e:
            self.asi.log(f"Trace failed for {ip}: {e}")
            return -1

    def block_ip_firewall(self, ip):
        try:
            if os.name == 'nt':
                cmd = f'netsh advfirewall firewall add rule name="HopperBlock {ip}" dir=out action=block remoteip={ip}'
            else:
                cmd = f'sudo iptables -A OUTPUT -d {ip} -j DROP'
            subprocess.call(cmd, shell=True)
            self.asi.log(f"IP {ip} blocked via firewall.")
        except Exception as e:
            self.asi.log(f"Firewall block error: {e}")

    def evaluate_ip(self, ip):
        country = self.get_country(ip)
        speak("Hopper path change detected.", 'sentinel')
        speak(f"Foreign destination: {country}", 'overseer')

        hops = self.trace_hops(ip)
        mood = 'green' if hops < 5 else 'orange' if hops <= 10 else 'red'
        status = 'stable' if mood == 'green' else 'unstable' if mood == 'orange' else 'hostile'
        self.asi.escalate_mood(mood)

        speak(f"{hops} hops detected. Threat status: {status}", 'overseer' if mood == 'red' else 'muse')
        if mood == 'red':
            self.block_ip_firewall(ip)

        self.cache[ip] = {
            'hops': hops,
            'country': country,
            'status': status,
            'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        self.save_cache()
        return ip, f"{hops} hops [{mood}] → {status}"

    def scan_outbound(self):
        outbound = [c for c in psutil.net_connections(kind='inet') if c.status == 'ESTABLISHED' and c.raddr]
        results = {}
        with ThreadPoolExecutor(max_workers=6) as executor:
            futures = {executor.submit(self.evaluate_ip, c.raddr.ip): c.raddr.ip for c in outbound}
            for future in as_completed(futures):
                ip, info = future.result()
                results[ip] = info
        return results

    def load_graph(self, path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    src, dst, weight = line.strip().split(',')
                    self.G.add_edge(src, dst, weight=int(weight))
            self.asi.log(f"Graph loaded: {path}")
        except Exception as e:
            self.asi.log(f"Graph load error: {e}")

    def shortest_hop(self, start, end):
        try:
            path = nx.shortest_path(self.G, source=start, target=end, weight='weight')
            self.asi.log(f"{start} → {end} path: {path}")
            return path
        except Exception as e:
            self.asi.log(f"Hop fail: {e}")
            return []

    def auto_loop(self, interval=600):
        while True:
            self.asi.log("Auto optimization cycle started.")
            self.scan_outbound()
            self.asi.log(f"Sleeping {interval} seconds...")
            time.sleep(interval)

# === GUI Interface ===
import tkinter as tk
from tkinter import filedialog, messagebox
import threading

class OvermindGUI:
    def __init__(self, hopper):
        self.hopper = hopper
        self.root = tk.Tk()
        self.root.title("🧠 Overmind Hopper Guardian GUI")
        self.root.geometry("580x460")
        self.root.configure(bg="#1a1d2d")
        self.build_ui()

    def build_ui(self):
        tk.Label(self.root, text="Start Node:", bg="#1a1d2d", fg="white").pack()
        self.start_entry = tk.Entry(self.root)
        self.start_entry.pack()

        tk.Label(self.root, text="End Node:", bg="#1a1d2d", fg="white").pack()
        self.end_entry = tk.Entry(self.root)
        self.end_entry.pack()

        tk.Button(self.root, text="📁 Load Graph", command=self.load_graph).pack(pady=5)
        tk.Button(self.root, text="↯ Shortest Hop", command=self.find_hop).pack(pady=5)
        tk.Button(self.root, text="🚀 Scan & Optimize", command=self.scan_optimize).pack(pady=5)
        tk.Button(self.root, text="📜 Show ASI Logs", command=self.show_logs).pack(pady=5)
        tk.Button(self.root, text="🔁 Start Auto Optimization", command=self.start_loop).pack(pady=5)

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
        messagebox.showinfo("System Scan", display or "No outbound connections found.")

    def show_logs(self):
        logs = self.hopper.asi.get_logs()
        messagebox.showinfo("ASI Tracker Logs", logs)

    def start_loop(self):
        threading.Thread(target=self.hopper.auto_loop, daemon=True).start()
        messagebox.showinfo("Auto Optimization", "Loop started. Will run every 10 mins.")

    def run(self):
        self.root.mainloop()

# === Launcher ===
if __name__ == "__main__":
    print("[BOOT] Overmind Hopper Unified Interface Online 🚀")
    asi = ASILogger()
    hopper = OvermindGuardian(asi)
    gui = OvermindGUI(hopper)
    gui.run()

