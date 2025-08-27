# dashboard.py

import time, threading, json, os
from random import choice, randint
import tkinter as tk
from tkinter import messagebox

from pulse import DataPulse
from mutation import MutationEvent, initiate_mutation_vote
from codex import store_mutation, CODEX_FILE
from node import Node
from fusion import FusionSignature
from portstream import generate_port_pulses, fuse_ports_by_process

class MagicBoxDashboard:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox System Monitor")
        self.root.geometry("1200x800")

        self.dark_mode = tk.BooleanVar(value=True)
        self.lineage_visible = tk.BooleanVar(value=False)
        self.auto_sync_enabled = tk.BooleanVar(value=True)

        self.theme_colors = {
            "dark": {"bg": "#1e1e2f", "canvas": "#2b2b3d", "text": "white"},
            "light": {"bg": "#f0f0f0", "canvas": "#ffffff", "text": "#222222"}
        }

        self.nodes = {}
        self.entropy_log = []

        self.canvas = tk.Canvas(self.root, width=1180, height=650)
        self.canvas.pack(pady=10)

        self.control_panel()
        self.apply_theme()

        threading.Thread(target=self.stream_pulses, daemon=True).start()
        self.root.mainloop()

    def apply_theme(self):
        mode = "dark" if self.dark_mode.get() else "light"
        colors = self.theme_colors[mode]
        self.root.configure(bg=colors["bg"])
        self.canvas.configure(bg=colors["canvas"])
        self.text_color = colors["text"]

    def control_panel(self):
        panel = tk.Frame(self.root)
        panel.pack()

        tk.Checkbutton(panel, text="🔗 Show Lineage", variable=self.lineage_visible,
                       font=("Consolas", 10)).pack(side="left", padx=10)

        tk.Checkbutton(panel, text="🔄 Auto-Sync Mode", variable=self.auto_sync_enabled,
                       font=("Consolas", 10)).pack(side="left", padx=10)

        tk.Button(panel, text="🎞️ Playback Mutations", command=self.playback_mutations,
                  font=("Consolas", 10)).pack(side="left", padx=10)

        tk.Button(panel, text="🌗 Toggle Theme", command=self.toggle_theme,
                  font=("Consolas", 10)).pack(side="left", padx=10)

    def toggle_theme(self):
        self.dark_mode.set(not self.dark_mode.get())
        self.apply_theme()

    def stream_pulses(self):
        while True:
            if not self.auto_sync_enabled.get():
                time.sleep(1.5)
                continue

            port_pulses = generate_port_pulses()
            fusion_map = fuse_ports_by_process([{
                "port": int(p.source.split("_")[1]),
                "name": getattr(p, "process_name", "unknown"),
                "proto": getattr(p, "protocol", "TCP")
            } for p in port_pulses])

            for pulse in port_pulses:
                node_id = pulse.source
                if node_id not in self.nodes:
                    self.nodes[node_id] = Node(node_id)
                node = self.nodes[node_id]

                node.pulses.append(pulse)
                node.last_entropy = pulse.entropy
                node.memory.record_pulse(pulse)
                self.entropy_log.append(pulse.entropy)

                if self.detect_density_spike(node.pulses) and node.personality.curiosity > 0.2:
                    votes, passed = initiate_mutation_vote()
                    mutation = MutationEvent(node_id, pulse.entropy, time.strftime("%H:%M:%S"), votes)
                    node.mutations.append(mutation)
                    node.memory.record_mutation(mutation)
                    store_mutation(mutation.__dict__)
                    node.fusion = FusionSignature(node_id, node.lineage, [p.entropy for p in node.pulses[-10:]])

            self.render_dashboard(fusion_map)
            time.sleep(2)

    def detect_density_spike(self, pulses):
        if len(pulses) < 10:
            return False
        recent = pulses[-10:]
        entropies = [p.entropy for p in recent]
        avg = sum(entropies) / len(entropies)
        variance = max(entropies) - min(entropies)
        return variance > 2.5 and avg > 7.0

    def render_dashboard(self, fusion_map):
        self.canvas.delete("all")
        positions = {}
        all_nodes = list(self.nodes.items())
        for i, (node_id, node) in enumerate(all_nodes):
            x = 160 + (i % 4) * 250
            y = 160 + (i // 4) * 180
            positions[node_id] = (x, y)
            self.draw_node(node, x, y)

        # 🎛️ Draw daemon fusion nodes with dynamic wrapping
        max_per_row = self.canvas.winfo_width() // 220
        for i, (proc_name, ports) in enumerate(fusion_map.items()):
            x = 100 + (i % max_per_row) * 220
            y = 40 + (i // max_per_row) * 60
            self.canvas.create_text(x, y, text=f"🧬 {proc_name}", fill="#00ffd0", font=("Consolas", 10))
            self.canvas.create_oval(x-10, y-10, x+10, y+10, fill="#444466", outline="#00ffd0", width=2)

            if self.lineage_visible.get():
                for port_entry in ports:
                    port_id = f"port_{port_entry['port']}_{port_entry['proto']}"
                    if port_id in positions:
                        x2, y2 = positions[port_id]
                        self.canvas.create_line(x, y, x2, y2, fill="#00ffd0", width=1, dash=(2, 2))

    def draw_node(self, node, x, y):
        entropy = node.last_entropy
        radius = int(10 + entropy * 2)
        proto = getattr(node.pulses[-1], "protocol", "TCP") if node.pulses else "TCP"
        border_style = (4, 2) if proto == "UDP" else None
        color = "#00ffd0" if entropy > 7 else "#ffaa00" if entropy > 5 else "#444466"

        self.canvas.create_oval(x-radius, y-radius, x+radius, y+radius,
                                fill=color, outline="#ffffff", width=2, dash=border_style)

        self.canvas.create_text(x, y+radius+10, text=f"{node.id}\n{entropy:.2f}",
                                fill=self.text_color, font=("Consolas", 9))

        if node.fusion:
            # Optional: draw fusion glyphs or lineage arcs here
            pass

    def playback_mutations(self):
        messagebox.showinfo("Playback", "Mutation playback not yet implemented.")

