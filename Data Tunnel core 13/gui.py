import tkinter as tk
from datetime import datetime
from network import get_active_streams
from ports import scan_active_ports
from personas import inject_decoy_persona, detect_genre
from codex import log_event, log_mutation
from asi import detect_density_spike, initiate_mutation_vote, rewrite_optimization_logic

# 🎨 GUI Theme
BG_COLOR = "#0b0c10"
TEXT_COLOR = "#c5c6c7"
ACTIVE_COLOR = "#66fcf1"
ENCRYPT_COLOR = "#00ffff"
BASE_RADIUS = 50

class TunnelCoreGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("TUNNELCORE: Port-Aware Vortex Edition")
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
        active_streams = get_active_streams()
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
            genre = detect_genre(active_streams)
            inject_decoy_persona(self.canvas, genre)
            scan_active_ports(self.canvas)

    def log_encryption_event(self, tunnel_count):
        entry = {
            "event": "encryption_perimeter_activated",
            "tunnel_count": tunnel_count,
            "timestamp": datetime.now().isoformat()
        }
        log_event(entry)

    def fade_out(self, ring, text):
        self.canvas.delete(ring)
        self.canvas.delete(text)

    def autonomous_loop(self):
        self.status_label.config(text="Status: Scanning Interfaces + Ports...")
        self.pulse_recursive_tunnels()
        if detect_density_spike(self.flow_history):
            self.status_label.config(text="Status: ASI Rewrite Triggered")
            if initiate_mutation_vote():
                rewrite = rewrite_optimization_logic()
                log_mutation(rewrite)
        self.root.after(5000, self.autonomous_loop)

