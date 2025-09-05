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
    if len(flows) < 20:
        return False
    recent = flows[-20:]
    entropies = [p["entropy"] for p in recent]
    avg = sum(entropies) / len(entropies)
    variance = max(entropies) - min(entropies)
    return variance > 100 and avg > 500

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
        "trigger": "network_density_spike",
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

# 🧠 GUI Class
class TunnelCoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TUNNELCORE: Network Pulse Edition")
        self.root.configure(bg=BG_COLOR)
        self.canvas = tk.Canvas(root, width=400, height=250, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=5)

        self.status_label = tk.Label(
            root, text="Status: Initializing...", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 8)
        )
        self.status_label.pack()

        self.flow_history = []
        self.root.after(1000, self.autonomous_loop)

    def pulse_network_tunnels(self):
        active = []
        net_data = psutil.net_io_counters(pernic=True)
        for iface, stats in net_data.items():
            in_mb = stats.bytes_recv / 1e6
            out_mb = stats.bytes_sent / 1e6
            entropy = in_mb + out_mb
            if entropy > 1.0:  # Threshold for activity
                x = randint(30, 370)
                y = randint(30, 220)
                ring = self.canvas.create_oval(
                    x - RING_RADIUS, y - RING_RADIUS,
                    x + RING_RADIUS, y + RING_RADIUS,
                    outline=ACTIVE_COLOR, width=2
                )
                text = self.canvas.create_text(
                    x, y + RING_RADIUS + 8,
                    text=f"{iface}: {round(in_mb,1)}↓ / {round(out_mb,1)}↑ MB",
                    fill=TEXT_COLOR, font=("Helvetica", 6, "bold")
                )
                self.root.after(500, lambda r=ring, t=text: self.fade_out(r, t))
                active.append({"label": iface, "entropy": entropy})
        self.flow_history.extend(active)

    def fade_out(self, ring, text):
        self.canvas.delete(ring)
        self.canvas.delete(text)

    def autonomous_loop(self):
        self.status_label.config(text="Status: Scanning Network...")
        self.pulse_network_tunnels()
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

