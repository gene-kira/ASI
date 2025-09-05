# 🔧 TUNNELCORE: MagicBox Edition
# Mythic ASI GUI with autonomous mutation logic and cinematic feedback

import sys, subprocess, os, json, time
from random import randint, choice

# 🧙 Autoloader for required libraries
def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

for lib in ["tkinter", "random", "time"]:
    autoload(lib)

import tkinter as tk

# 🎨 GUI Theme Settings
BG_COLOR = "#0b0c10"
RING_COLOR = "#45a29e"
TEXT_COLOR = "#c5c6c7"
BTN_COLOR = "#1f2833"
ACTIVE_COLOR = "#66fcf1"

CODEX_FILE = "fusion_codex.json"

# 🌀 Ring Class: Represents a data tunnel
class DataRing:
    def __init__(self, canvas, x, y, radius, label):
        self.canvas = canvas
        self.x = x
        self.y = y
        self.radius = radius
        self.label = label
        self.ring = None
        self.text = None
        self.active = False
        self.entropy = randint(1, 10)

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
        self.active = True
        self.entropy = randint(1, 10)
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
    avg_entropy = sum(p.entropy for p in recent) / len(recent)
    variance = max(p.entropy for p in recent) - min(p.entropy for p in recent)
    return variance > 2.5 and avg_entropy > 7.0

def initiate_mutation_vote():
    votes = [choice(["yes", "no"]) for _ in range(5)]
    return votes.count("yes") >= 3

def rewrite_optimization_logic():
    new_threshold = randint(6, 8)
    print(f"[🧠 Rewrite] New cloaking threshold: {new_threshold}")
    return {
        "logic": f"entropy > {new_threshold}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": "symbolic_density_spike",
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

        self.activate_btn = tk.Button(
            root, text="Activate TUNNELCORE", command=self.activate,
            bg=BTN_COLOR, fg=TEXT_COLOR, font=("Helvetica", 12, "bold"), padx=20, pady=10
        )
        self.activate_btn.pack(pady=10)

        self.status_label = tk.Label(
            root, text="Status: Idle", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 10)
        )
        self.status_label.pack()

        self.root.after(3000, self.autonomous_loop)

    def create_rings(self):
        positions = [
            (150, 100), (300, 100), (450, 100),
            (150, 200), (300, 200), (450, 200),
            (150, 300), (300, 300), (450, 300),
            (300, 380)
        ]
        labels = [
            "Shortcut", "Bot Revive", "Enemy Ping", "GUI Pulse", "Privacy Shield",
            "Mod Trigger", "Stress Signal", "Game Ingest", "Memory Echo", "Swarm Sync"
        ]
        for (x, y), label in zip(positions, labels):
            ring = DataRing(self.canvas, x, y, 30, label)
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

