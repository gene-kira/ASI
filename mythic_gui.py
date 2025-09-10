# mythic_gui.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

# Core Modules (simplified for GUI integration)
class IngestMonitor:
    def __init__(self):
        self.threats = []

    def ingest(self, data):
        timestamp = datetime.utcnow()
        threat_type = self.detect_threat(data)
        if threat_type:
            self.threats.append((timestamp, threat_type, data))
        return threat_type

    def detect_threat(self, data):
        if "phantom" in data or "backdoor" in data:
            return "backdoor"
        elif "MAC:" in data or "IP:" in data:
            return "network"
        elif "telemetry" in data:
            return "telemetry"
        elif "ghost sync" in data:
            return "ghost sync"
        return None

class CodexEngine:
    def __init__(self):
        self.retention = timedelta(minutes=5)
        self.mutations = []

    def mutate(self, threat_type):
        if threat_type == "ghost sync":
            self.retention = timedelta(minutes=1)
            self.mutations.append(f"{datetime.utcnow()}: Codex mutated due to ghost sync.")

class Persona:
    def __init__(self, name):
        self.name = name
        self.arc = []

    def narrate(self, event):
        self.arc.append(f"{datetime.utcnow()}: {self.name} - {event}")

class SymbolicLog:
    def __init__(self):
        self.entries = []

    def log(self, message):
        entry = f"{datetime.utcnow()}: {message}"
        self.entries.append(entry)
        return entry

# GUI Application
class MythicNodeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MythicNode Defense Grid")
        self.geometry("1000x600")
        self.configure(bg="#1e1e1e")

        # DPI-aware scaling
        self.tk.call('tk', 'scaling', 1.5)

        # Core modules
        self.ingest_monitor = IngestMonitor()
        self.codex = CodexEngine()
        self.personas = [Persona("ThreatHunter"), Persona("Compliance Auditor")]
        self.log = SymbolicLog()

        # GUI Panels
        self.create_panels()

    def create_panels(self):
        # Ingest Panel
        ingest_frame = ttk.LabelFrame(self, text="Ingest Monitor")
        ingest_frame.pack(fill="x", padx=10, pady=5)
        self.ingest_entry = ttk.Entry(ingest_frame, width=80)
        self.ingest_entry.pack(side="left", padx=5)
        ttk.Button(ingest_frame, text="Ingest", command=self.handle_ingest).pack(side="left")

        # Threat Matrix
        self.threat_list = tk.Listbox(self, height=6, bg="#2e2e2e", fg="white")
        self.threat_list.pack(fill="x", padx=10, pady=5)

        # Codex Mutation Log
        codex_frame = ttk.LabelFrame(self, text="Codex Mutation Log")
        codex_frame.pack(fill="x", padx=10, pady=5)
        self.codex_log = tk.Text(codex_frame, height=6, bg="#2e2e2e", fg="white")
        self.codex_log.pack(fill="x")

        # Persona Arc
        persona_frame = ttk.LabelFrame(self, text="Persona Arcs")
        persona_frame.pack(fill="x", padx=10, pady=5)
        self.persona_log = tk.Text(persona_frame, height=6, bg="#2e2e2e", fg="white")
        self.persona_log.pack(fill="x")

        # Symbolic Feedback
        feedback_frame = ttk.LabelFrame(self, text="Symbolic Feedback")
        feedback_frame.pack(fill="both", expand=True, padx=10, pady=5)
        self.feedback_log = tk.Text(feedback_frame, bg="#2e2e2e", fg="white")
        self.feedback_log.pack(fill="both", expand=True)

    def handle_ingest(self):
        data = self.ingest_entry.get()
        threat_type = self.ingest_monitor.ingest(data)
        if threat_type:
            self.threat_list.insert(tk.END, f"{datetime.utcnow()}: {threat_type}")
            self.codex.mutate(threat_type)
            for mutation in self.codex.mutations:
                self.codex_log.insert(tk.END, mutation + "\n")
            for persona in self.personas:
                persona.narrate(f"Intercepted {threat_type}")
                self.persona_log.insert(tk.END, persona.arc[-1] + "\n")
            feedback = self.log.log(f"Threat classified: {threat_type}")
            self.feedback_log.insert(tk.END, feedback + "\n")
        else:
            feedback = self.log.log("No threat detected.")
            self.feedback_log.insert(tk.END, feedback + "\n")

# Run GUI
if __name__ == "__main__":
    app = MythicNodeGUI()
    app.mainloop()

