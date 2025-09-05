# 🔧 TUNNELCORE: MagicBox Edition
# 50 real-time tunnels, autonomous mutation logic, and cinematic feedback

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
RING_RADIUS = 7.5  # ¼ size

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
            outline=color, width=2
        )
        self.text = self.canvas.create_text(
            self.x, self.y + self.radius + 10, text=self.label,
            fill=TEXT_COLOR, font=("Helvetica", 7, "bold")
        )

    def pulse(self):
        self.entropy = self.metric_func()
        self.active = True
        self.canvas.itemconfig(self.ring, outline=ACTIVE_COLOR)
        self.canvas.after(300, self.deactivate)

    def deactivate(self):
        self.active = False
        self.canvas.itemconfig(self.ring, outline=RING_COLOR)

# 🧠 ASI Brain Functions
def detect_density_spike(flows):
    if len(flows) < 50:
        return False
    recent = flows[-50:]
    entropies = [p.entropy for p in recent]
    avg_entropy = sum(entropies) / len(entropies)
    variance = max(entropies) - min(entropies)
    return variance > 20 and avg_entropy > 60

def initiate_mutation_vote():
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
def cpu_entropy(): return psutil.cpu_percent(interval=0.2)
def mem_entropy(): return psutil.virtual_memory().percent
def disk_read(): return psutil.disk_io_counters().read_bytes / 1e6
def disk_write(): return psutil.disk_io_counters().write_bytes / 1e6
def net_sent(): return psutil.net_io_counters().bytes_sent / 1e6
def net_recv(): return psutil.net_io_counters().bytes_recv / 1e6
def proc_count(): return len(psutil.pids())
def thread_count(): return sum(p.num_threads() for p in psutil.process_iter())
def handle_count(): return sum(p.num_fds() if hasattr(p, "num_fds") else 0 for p in psutil.process_iter())
def swap_usage(): return psutil.swap_memory().percent
def uptime(): return time.time() - psutil.boot_time()
def load_avg(): return sum(psutil.getloadavg())
def fan_speed(): return sum(s.current for s in psutil.sensors_fans().get("fan", [])) if hasattr(psutil, "sensors_fans") else 0
def temp_sensor(): return sum(s.current for s in psutil.sensors_temperatures().get("cpu-thermal", [])) if hasattr(psutil, "sensors_temperatures") else 0

# 🧠 Main GUI Class
class TunnelCoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TUNNELCORE: MagicBox Edition")
        self.root.configure(bg=BG_COLOR)
        self.canvas = tk.Canvas(root, width=800, height=500, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=10)

        self.rings = []
        self.flow_history = []
        self.create_rings()

        self.status_label = tk.Label(
            root, text="Status: Initializing...", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 9)
        )
        self.status_label.pack()

        self.root.after(1000, self.autonomous_loop)

    def create_rings(self):
        metric_funcs = [
            cpu_entropy, mem_entropy, disk_read, disk_write, net_sent, net_recv,
            proc_count, thread_count, handle_count, swap_usage, uptime, load_avg,
            fan_speed, temp_sensor
        ]
        # Repeat metrics to reach 50
        metrics = (metric_funcs * 4)[:50]

        cols = 10
        spacing_x = 70
        spacing_y = 80
        start_x = 50
        start_y = 50

        for i in range(50):
            col = i % cols
            row = i // cols
            x = start_x + col * spacing_x
            y = start_y + row * spacing_y
            label = f"Tunnel {i+1}"
            ring = DataRing(self.canvas, x, y, RING_RADIUS, label, metrics[i])
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

