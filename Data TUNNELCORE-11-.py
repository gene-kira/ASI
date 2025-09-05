import sys, subprocess, os, json, time
from datetime import datetime
from random import choice

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
TEXT_COLOR = "#c5c6c7"
ACTIVE_COLOR = "#66fcf1"
ENCRYPT_COLOR = "#00ffff"
CODEX_FILE = "fusion_codex.json"
BASE_RADIUS = 50

# 🧠 Codex Logging
def store_codex_event(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

# 🔐 Persona Definitions
PERSONAS = {
    "Gaming": {"name": "SquadSyncBot", "color": "#ff9900"},
    "Finance": {"name": "LedgerPhantom", "color": "#33cc33"},
    "Medical": {"name": "PulseEcho", "color": "#cc66ff"},
    "Social": {"name": "GhostContact", "color": "#66cccc"},
    "Default": {"name": "NullPacket", "color": "#999999"}
}

# 🧠 ASI Brain
def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    entropies = [f["entropy"] for f in recent]
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
        "trigger": "recursive_density_spike",
        "consensus": "mutation_vote_passed"
    }

# 🧠 GUI Class
class TunnelCoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TUNNELCORE: Decoy Persona Edition")
        self.root.configure(bg=BG_COLOR)
        self.canvas = tk.Canvas(root, width=400, height=250, bg=BG_COLOR, highlightthickness=0)
        self.canvas.pack(pady=5)

        self.status_label = tk.Label(
            root, text="Status: Initializing...", bg=BG_COLOR, fg=TEXT_COLOR, font=("Helvetica", 8)
        )
        self.status_label.pack()

        self.flow_history = []
        self.root.after(1000, self.autonomous_loop)

    def pulse_recursive_tunnels(self):
        net_data = psutil.net_io_counters(pernic=True)
        active_streams = []
        for iface, stats in net_data.items():
            in_mb = stats.bytes_recv / 1e6
            out_mb = stats.bytes_sent / 1e6
            entropy = in_mb + out_mb
            if entropy > 1.0:
                active_streams.append({
                    "iface": iface,
                    "in_mb": round(in_mb, 1),
                    "out_mb": round(out_mb, 1),
                    "entropy": entropy
                })

        center_x, center_y = 200, 125
        for i, stream in enumerate(active_streams):
            radius = BASE_RADIUS * (0.9 ** i)
            color = ENCRYPT_COLOR if i == 0 else ACTIVE_COLOR
            label = "Encrypted Perimeter" if i == 0 else f"{stream['iface']}: {stream['in_mb']}↓ / {stream['out_mb']}↑ MB"
            ring = self.canvas.create_oval(
                center_x - radius, center_y - radius,
                center_x + radius, center_y + radius,
                outline=color, width=2
            )
            text = self.canvas.create_text(
                center_x, center_y + radius + 10,
                text=label, fill=TEXT_COLOR, font=("Helvetica", 6, "bold")
            )
            self.root.after(600, lambda r=ring, t=text: self.fade_out(r, t))
            self.flow_history.append(stream)

        if active_streams:
            self.log_encryption_event(len(active_streams))
            self.inject_decoy_persona(active_streams)

    def log_encryption_event(self, tunnel_count):
        entry = {
            "event": "encryption_perimeter_activated",
            "tunnel_count": tunnel_count,
            "timestamp": datetime.now().isoformat()
        }
        store_codex_event(entry)
        print(f"[🔐] Encryption perimeter enforced for {tunnel_count} tunnels")

    def inject_decoy_persona(self, streams):
        genre = self.detect_genre(streams)
        persona = PERSONAS.get(genre, PERSONAS["Default"])
        color = persona["color"]
        name = persona["name"]

        ring = self.canvas.create_oval(
            180, 105, 220, 145,
            outline=color, width=2
        )
        text = self.canvas.create_text(
            200, 155,
            text=name, fill=TEXT_COLOR, font=("Helvetica", 6, "italic")
        )
        self.root.after(30000, lambda: self.fade_out(ring, text))
        entry = {
            "event": "decoy_persona_discarded",
            "persona": name,
            "genre": genre,
            "reason": "expired 30s lifecycle",
            "timestamp": datetime.now().isoformat()
        }
        store_codex_event(entry)
        print(f"[🕵️] Decoy persona '{name}' injected for genre '{genre}'")

    def detect_genre(self, streams):
        labels = " ".join([s["iface"].lower() for s in streams])
        if any(k in labels for k in ["game", "steam", "epic"]): return "Gaming"
        if any(k in labels for k in ["bank", "finance", "ledger"]): return "Finance"
        if any(k in labels for k in ["med", "pulse", "bio"]): return "Medical"
        if any(k in labels for k in ["social", "msg", "chat"]): return "Social"
        return "Default"

    def fade_out(self, ring, text):
        self.canvas.delete(ring)
        self.canvas.delete(text)

    def autonomous_loop(self):
        self.status_label.config(text="Status: Scanning Interfaces...")
        self.pulse_recursive_tunnels()
        if detect_density_spike(self.flow_history):
            self.status_label.config(text="Status: ASI Rewrite Triggered")
            if initiate_mutation_vote():
                rewrite = rewrite_optimization_logic()
                store_codex_event(rewrite)
                print(f"[✅] Mutation stored: {rewrite['logic']}")
        self.root.after(5000, self.autonomous_loop)

# 🚀 Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = TunnelCoreGUI(root)
    root.mainloop()

