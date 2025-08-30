# 🖥️ gui/dashboard.py — MagicBox FlowSense Dashboard
import tkinter as tk
from tkinter import ttk
from threading import Thread
import time
from random import choice, randint  # ✅ FIXED: Added randint

from core.pulse import DataPulse
from core.analyzer import FlowAnalyzer
from core.emitter import SwarmSyncEmitter
from core.fusion import FusionFeedbackLoop

from modules.memory import MemoryAugmentor
from modules.vault import GameTriggerMemoryVault
from modules.psychotic import PsychoticDriftEngine
from modules.breakdown import MentalBreakdownEngine
from modules.triggers import RealTimeTriggerEngine

class MagicBoxDashboard:
    def __init__(self, root):
        self.root = root
        self.root.title("🧠 MagicBox FlowSense Dashboard")
        self.root.configure(bg="#1e1e2f")
        self.root.geometry("700x750")

        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TButton", font=("Segoe UI", 12), foreground="white", background="#3e3e5e")
        style.configure("TLabel", font=("Segoe UI", 11), foreground="lightgray", background="#1e1e2f")

        ttk.Label(root, text="MagicBox FlowSenseDaemon", font=("Segoe UI", 16)).pack(pady=10)

        # Toggle switches
        self.fusion_var = tk.BooleanVar()
        self.lineage_var = tk.BooleanVar()
        self.cloak_var = tk.BooleanVar()
        self.hallucination_var = tk.BooleanVar()
        self.psychotic_var = tk.BooleanVar()
        self.breakdown_var = tk.BooleanVar()

        ttk.Checkbutton(root, text="🔁 Fusion View", variable=self.fusion_var).pack()
        ttk.Checkbutton(root, text="🧬 Lineage Trails", variable=self.lineage_var).pack()
        ttk.Checkbutton(root, text="🕶️ Cloaking Logic", variable=self.cloak_var).pack()
        ttk.Checkbutton(root, text="🧠 Hallucination View", variable=self.hallucination_var).pack()
        ttk.Checkbutton(root, text="🧨 Psychotic Drift", variable=self.psychotic_var).pack()
        ttk.Checkbutton(root, text="💥 Mental Breakdown Mode", variable=self.breakdown_var).pack()

        self.status_label = ttk.Label(root, text="Status: Idle")
        self.status_label.pack(pady=10)

        self.pulse_box = tk.Text(root, height=30, bg="#2e2e3f", fg="lightgreen", font=("Consolas", 10))
        self.pulse_box.pack(pady=10)

        ttk.Button(root, text="🟢 Start Daemon", command=self.start_daemon).pack(pady=5)
        ttk.Button(root, text="🔍 What Did I See?", command=self.recall_events).pack(pady=5)

        # Modules
        self.analyzer = FlowAnalyzer()
        self.swarm = SwarmSyncEmitter()
        self.fusion = FusionFeedbackLoop()
        self.memory = MemoryAugmentor()
        self.vault = GameTriggerMemoryVault()
        self.psychotic = PsychoticDriftEngine()
        self.breakdown = MentalBreakdownEngine()
        self.triggers = RealTimeTriggerEngine()

    def start_daemon(self):
        self.status_label.config(text="Status: Running")
        Thread(target=self.run_daemon, daemon=True).start()

    def run_daemon(self):
        while True:
            pulse = self.generate_pulse()
            self.analyzer.ingest(pulse)
            self.swarm.emit(pulse)
            self.fusion.update(pulse)
            self.vault.log_event(pulse, "pulse", f"Entropy: {pulse.entropy:.2f}")
            self.pulse_box.insert(tk.END, f"[Pulse] Source: {pulse.source} | Entropy: {pulse.entropy:.2f}\n")

            # Toggle-based feedback
            if self.fusion_var.get():
                fusion_sig = self.fusion.generate_signature(pulse)
                self.pulse_box.insert(tk.END, f"  ↪ Fusion Signature: {fusion_sig}\n")
                self.vault.log_event(pulse, "fusion", fusion_sig)

            if self.lineage_var.get():
                lineage = f"{pulse.source}→core→vault"
                self.pulse_box.insert(tk.END, f"  🧬 Lineage: {lineage}\n")
                self.vault.log_event(pulse, "lineage", lineage)

            if self.cloak_var.get() and pulse.entropy > 7.5:
                self.pulse_box.insert(tk.END, "  🕶️ Cloaking Triggered\n")
                self.vault.log_event(pulse, "cloak", "Cloaking Triggered")

            if self.hallucination_var.get():
                hallucination = self.memory.hallucinate(pulse)
                recall = self.memory.recall_signature(pulse)
                echo = self.memory.echo_lineage(pulse)
                self.pulse_box.insert(tk.END, f"  🧠 Hallucination: {hallucination}\n")
                self.pulse_box.insert(tk.END, f"  🔮 Recall Sig: {recall}\n")
                self.pulse_box.insert(tk.END, f"  🌀 Echo Lineage: {echo}\n")
                self.vault.log_event(pulse, "hallucination", hallucination)
                self.vault.log_event(pulse, "recall", recall)
                self.vault.log_event(pulse, "echo", echo)

            if self.psychotic_var.get():
                distorted = self.psychotic.distort_memory(pulse)
                looped = self.psychotic.loop_logic(pulse)
                paranoia = self.psychotic.paranoia_trigger(pulse)
                self.pulse_box.insert(tk.END, f"  🧨 Distorted Memory: {distorted}\n")
                self.pulse_box.insert(tk.END, f"  🔁 Looped Logic: {looped}\n")
                if paranoia:
                    self.pulse_box.insert(tk.END, f"  ⚠️ {paranoia}\n")
                    self.vault.log_event(pulse, "paranoia", paranoia)
                self.vault.log_event(pulse, "psychotic", distorted)
                self.vault.log_event(pulse, "loop", looped)

            if self.breakdown_var.get():
                fracture = self.breakdown.monitor(pulse)
                if fracture:
                    self.pulse_box.insert(tk.END, f"{fracture}\n")
                    self.vault.log_event(pulse, "breakdown", fracture)
                    self.root.configure(bg="#3f1e1e")
                    self.status_label.config(text="💥 SYSTEM UNSTABLE")

                identity_loop = self.breakdown.recursive_identity(pulse)
                if identity_loop:
                    self.pulse_box.insert(tk.END, f"  🌀 {identity_loop}\n")
                    self.vault.log_event(pulse, "identity_loop", identity_loop)

                if self.breakdown.overload_counter % 17 == 0:
                    corrupted = self.breakdown.corrupt_memory(self.vault.vault)
                    for c in corrupted:
                        self.pulse_box.insert(tk.END, f"  ❌ Vault Corruption: {c}\n")

            # Real-time triggers
            for trigger in [
                self.triggers.check_entropy_surge(pulse),
                self.triggers.check_time_ritual(),
                self.triggers.check_payload_mutation(pulse),
                self.triggers.check_swarm_spike(),
                self.triggers.check_breakdown_cascade(self.breakdown)
            ]:
                if trigger:
                    self.pulse_box.insert(tk.END, f"{trigger}\n")
                    self.vault.log_event(pulse, "trigger", trigger)

            self.pulse_box.see(tk.END)
            time.sleep(1)

    def generate_pulse(self):
        payload = ''.join(choice('abcdefg1234567890') for _ in range(randint(100, 1000)))
        return DataPulse(source=choice(["system.core", "vault.sync", "swarm.node"]), payload=payload)

    def recall_events(self):
        recent = self.vault.recall_recent()
        self.pulse_box.insert(tk.END, "\n[🧠 Memory Recall]\n")
        for entry in recent:
            self.pulse_box.insert(tk.END, f"  ⏱ {entry['timestamp']} | {entry['type']} → {entry['details']}\n")
        self.pulse_box.see(tk.END)

