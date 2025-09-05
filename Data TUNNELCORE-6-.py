import sys, subprocess, os, json, time
from datetime import datetime
from random import randint

# 🧙 Autoloader
def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for lib in ["tkinter", "psutil"]:
    autoload(lib)

import tkinter as tk
import psutil

# 🎨 GUI Theme
BG_COLOR = "#0b0c10"
RING_COLOR = "#45a29e"
TEXT_COLOR = "#c5c6c7"
ACTIVE_COLOR = "#66fcf1"
CODEX_FILE = "fusion_codex.json"
RING_RADIUS = 7.5

# 🧠 ASI Brain
def detect_density_spike(flows):
    if len(flows) < 50:
        return False
    recent = flows[-50:]
    entropies = [p["entropy"] for p in recent]
    avg = sum(entropies) / len(entropies)
    variance = max(entropies) - min(entropies)
    return variance > 20 and avg > 60

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

# 🔍 Real-Time Metrics
def cpu(): return psutil.cpu_percent(interval=0.1)
def mem(): return psutil.virtual_memory().percent
def disk_r(): return psutil.disk_io_counters().read_bytes / 1e6
def disk_w(): return psutil.disk_io_counters().write_bytes / 1e6
def net_s(): return psutil.net_io_counters().bytes_sent / 1e6
def net_r(): return psutil.net_io_counters().bytes_recv / 1e6
def proc(): return len(psutil.pids())
def threads(): return sum(p.num_threads() for p in psutil.process_iter())
def handles(): return sum(p.num_fds() if hasattr(p, "num_fds") else 0 for p in psutil.process_iter())
def swap(): return psutil.swap_memory().percent
def uptime(): return time.time() - psutil.boot_time()
def load(): return sum(psutil.getloadavg())

metric_pool = [
    ("CPU Load", cpu),
    ("Memory Use", mem),
    ("Disk Read", disk_r),
    ("Disk Write", disk_w),
    ("Net Sent", net_s),
    ("Net Recv", net_r),
    ("Process Count", proc),
    ("Thread Count", threads),
    ("Handle Count", handles),
    ("Swap Use", swap),
    ("Uptime", uptime),
    ("Load Avg", load)
]

# 🧠 GUI Class
class TunnelCoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TUNNELCORE: MagicBox Edition")
        self.root.configure(bg=BG_COLOR)
        self.canvas = tk.Canvas(root, width=800, height=500, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=10)

        self.status_label = tk.Label(
            root, text="Status: Initializing...", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 9)
        )
        self.status_label.pack()

        self.flow_history = []
        self.root.after(1000, self.autonomous_loop)

    def pulse_tunnels(self):
        active = []
        for i in range(50):
            label, func = metric_pool[i % len(metric_pool)]
            entropy = func()
            if entropy > 50:
                x = randint(50, 750)
                y = randint(50, 450)
                ring = self.canvas.create_oval(
                    x - RING_RADIUS, y - RING_RADIUS,
                    x + RING_RADIUS, y + RING_RADIUS,
                    outline=ACTIVE_COLOR, width=2
                )
                text = self.canvas.create_text(
                    x, y + RING_RADIUS + 10,
                    text=f"{label}: {round(entropy, 1)}",
                    fill=TEXT_COLOR, font=("Helvetica", 7, "bold")
                )
                self.root.after(500, lambda r=ring, t=text: self.fade_out(r, t))
                active.append({"label": label, "entropy": entropy})
        self.flow_history.extend(active)

    def fade_out(self, ring, text):
        self.canvas.delete(ring)
        self.canvas.delete(text)

    def autonomous_loop(self):
        self.status_label.config(text="Status: Tunneling...")
        self.pulse_tunnels()
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

