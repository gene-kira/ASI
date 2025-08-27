# dashboard.py

import tkinter as tk
from tkinter import ttk
from threading import Thread
import time
from random import randint, choice

from pulse import DataPulse
from memory import (
    load_memory, save_memory, update_memory,
    is_known_game, recall_optimization, detect_mutation_spike
)
from engines import FlowAnalyzer, SwarmSyncEmitter, FusionFeedbackLoop
from visualizer import (
    animate_node_growth, draw_lineage_trail, draw_mutation_flare
)

class MagicBoxDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MagicBox FlowSense Dashboard")
        self.root.configure(bg="#1e1e2f")
        self.root.geometry("800x600")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12), foreground="white", background="#3e3e5e")
        style.configure("TLabel", font=("Segoe UI", 11), foreground="lightgray", background="#1e1e2f")

        ttk.Label(root, text="MagicBox FlowSenseDaemon", font=("Segoe UI", 16)).pack(pady=10)

        self.fusion_var = tk.BooleanVar(value=True)
        self.lineage_var = tk.BooleanVar(value=True)
        self.cloak_var = tk.BooleanVar(value=True)

        ttk.Checkbutton(root, text="🔁 Fusion View", variable=self.fusion_var).pack()
        ttk.Checkbutton(root, text="🧬 Lineage Trails", variable=self.lineage_var).pack()
        ttk.Checkbutton(root, text="🕶️ Cloaking Logic", variable=self.cloak_var).pack()

        self.status_label = ttk.Label(root, text="Status: Running")
        self.status_label.pack(pady=10)

        self.pulse_box = tk.Text(root, height=10, bg="#2e2e3f", fg="lightgreen", font=("Consolas", 10))
        self.pulse_box.pack(pady=10)

        self.canvas = tk.Canvas(root, width=760, height=200, bg="#1e1e2f", highlightthickness=0)
        self.canvas.pack(pady=10)

        self.analyzer = FlowAnalyzer()
        self.swarm = SwarmSyncEmitter()
        self.fusion = FusionFeedbackLoop()
        self.memory = load_memory()

        self.start_daemon()

    def start_daemon(self):
        Thread(target=self.run_daemon, daemon=True).start()

    def run_daemon(self):
        while True:
            pulse = self.generate_pulse()
            self.analyzer.ingest(pulse)

            if is_known_game(pulse, self.memory):
                recall = recall_optimization(pulse, self.memory)
                if recall:
                    self.pulse_box.insert(tk.END, f"{recall}\n")
            else:
                self.swarm.emit(pulse)
                self.fusion.update(pulse)
                update_memory(pulse, self.memory)

            self.pulse_box.insert(tk.END, f"[Pulse] Source: {pulse.source} | Entropy: {pulse.entropy:.2f}\n")
            if self.fusion_var.get():
                self.pulse_box.insert(tk.END, f"  ↪ Fusion Signature: {self.generate_fusion(pulse)}\n")
            if self.lineage_var.get():
                self.pulse_box.insert(tk.END, f"  🧬 Lineage: {self.generate_lineage(pulse)}\n")
            if self.cloak_var.get() and pulse.entropy > 7.5:
                self.pulse_box.insert(tk.END, "  🕶️ Cloaking Triggered\n")

            self.pulse_box.see(tk.END)
            self.memory = load_memory()
            self.draw_memory_density()
            time.sleep(1)

    def generate_pulse(self):
        payload = ''.join(choice('abcdefg1234567890') for _ in range(randint(100, 1000)))
        return DataPulse(source=choice(["game.exe", "vault.sync", "swarm.node"]), payload=payload)

    def generate_fusion(self, pulse):
        return f"F:{hash(pulse.source + str(pulse.entropy)) % 9999}"

    def generate_lineage(self, pulse):
        return f"L:{pulse.source}→core→vault"

    def draw_memory_density(self):
        self.canvas.delete("all")
        x = 50
        for proc, data in self.memory.items():
            count = len(data["entropy_profile"])
            avg_entropy = sum(data["entropy_profile"]) / count
            radius = min(10 + count * 2, 40)
            color = "#00ff00" if avg_entropy < 6 else "#ff9900" if avg_entropy < 7.5 else "#ff3333"

            animate_node_growth(self.canvas, self.root, proc, radius, color, x)

            if detect_mutation_spike(data["entropy_profile"]):
                draw_mutation_flare(self.canvas, x, radius)

            if self.lineage_var.get():
                draw_lineage_trail(self.canvas, data["lineage"], x)

            fusion = data.get("fusion_signature", "F:????")
            last_seen = data.get("last_seen", "unknown")
            self.canvas.create_text(x + radius / 2, 50 + radius + 10, text=proc, fill="white", font=("Segoe UI", 8))
            self.canvas.create_text(x + radius / 2, 50 + radius + 25, text=f"{fusion} | {last_seen}", fill="gray", font=("Consolas", 7))

            x += radius + 80

