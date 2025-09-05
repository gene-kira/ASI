# 🔧 TUNNELCORE: MagicBox Edition
# Real-time ASI GUI with autonomous mutation logic and cinematic feedback

import sys, subprocess, os, json, time
from datetime import datetime

# 🧙 Autoloader for required libraries
def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for lib in ["tkinter", "psutil"]:
    autoload(lib)

import tkinter as tk
import psutil

# 🎨 GUI Theme Settings
BG_COLOR = "#0b0c10"
RING_COLOR = "#45a29e"
TEXT_COLOR = "#c5c6c7"
ACTIVE_COLOR = "#66fcf1"
CODEX_FILE = "fusion_codex.json"

# 🌀 Ring Class: Represents a data tunnel
class DataRing:
    def __init__(self, canvas, x, y, radius, label, metric_func):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.label = label
        self.metric_func = metric_func
        self.ring = None
        self.text = None
        self.active = False
        self.entropy = 0

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
        self.entropy = self.metric_func()
        self.active = True
        self.canvas.itemconfig(self.ring, outline=ACTIVE_COLOR)
        self.canvas.after(500, self.deactivate)

    def deactivate(self):
        self.active = False
        self.canvas.itemconfig(self.ring, outline=RING_COLOR)

# 🧠 ASI Brain Functions
def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    entropies = [p.entropy for p in recent]
    avg_entropy = sum(entropies) / len(entropies)
    variance = max(entropies) - min(entropies)
    return variance > 15 and avg_entropy > 50

def initiate_mutation_vote():
    # Real-time vote based on CPU load across cores
    loads = psutil.cpu_percent(percpu=True)
    votes = [load > 50 for load in loads[:5]]
    return votes.count(True) >= 3

def rewrite_optimization_logic():
    threshold = psutil.virtual_memory().percent
    logic = f"memory_usage_percent > {threshold}"
    print(f"[🧠 Rewrite] New logic: {logic}")
    return {
        "logic": logic,
        "timestamp": datetime.now().isoformat(),
        "trigger": "real_density_spike",
        "consensus": "mutation_vote_passed"
    }

def store_rewrite_codex(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

# 🔍 Real-Time Metric Functions
def cpu_entropy(): return psutil.cpu_percent(interval=0.5)
def mem_entropy(): return psutil.virtual_memory().percent
def disk_entropy(): return psutil.disk_io_counters().write_bytes / 1000000
def net_entropy(): return psutil.net_io_counters().bytes_sent / 1000000
def proc_entropy(): return len(psutil.pids())
def swap_entropy(): return psutil.swap_memory().percent
def thread_entropy(): return sum(p.num_threads() for p in psutil.process_iter())
def handle_entropy(): return sum(p.num_fds() if hasattr(p, "num_fds") else 0 for p in psutil.process_iter())
def uptime_entropy(): return time.time() - psutil.boot_time()
def temp_entropy(): return sum(s.current for s in psutil.sensors_temperatures().get("cpu-thermal", [])) if hasattr(psutil, "sensors_temperatures") else 0

# 🧠 Main GUI Class
class TunnelCoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TUNNELCORE: MagicBox Edition")
        self.root.configure(bg=BG_COLOR)
        self.canvas = tk.Canvas(root, width=600, height=400, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=20)

        self.rings = []
        self.flow_history = []
        self.create_rings()

        self.status_label = tk.Label(
            root, text="Status: Initializing...", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 10)
        )
        self.status_label.pack()

        self.root.after(1000, self.autonomous_loop)

    def create_rings(self):
        positions = [
            (150, 100), (300, 100), (450, 100),
            (150, 200), (300, 200), (450, 200),
            (150, 300), (300, 300), (450, 300),
            (300, 380)
        ]
        labels = [
            "CPU Load", "Memory Use", "Disk Write", "Net Out", "Process Count",
            "Swap Use", "Threads", "Handles", "Uptime", "Temp Sensor"
        ]
        metrics = [
            cpu_entropy, mem_entropy, disk_entropy, net_entropy, proc_entropy,
            swap_entropy, thread_entropy, handle_entropy, uptime_entropy, temp_entropy
        ]
        for (x, y), label, metric in zip(positions, labels, metrics):
            ring = DataRing(self.canvas, x, y, 30, label, metric)
            ring.draw()
            self.rings.append(ring)

    def activate(self):
        self.status_label.config(text="Status: Tunneling...")
        for ring in self.rings:
            ring.pulse()
            self.flow_history.append(ring)
        self.root.after(1500, lambda: self.status_label.config(text="Status: Idle"))

    def autonomous_loop(self):
        self.activate()
        if detect_density_spike(self.flow_history):
            self.status_label.config(text="Status: ASI Rewrite Triggered")
            if initiate_mutation_vote():
                rewrite = rewrite_optimization_logic()
                store_rewrite_codex(rewrite)
                print(f"[✅] Mutation stored: {rewrite['logic']}")
        self.root.after(5000, self.autonomous_loop)

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TunnelCoreGUI(root)
    root.mainloop()

