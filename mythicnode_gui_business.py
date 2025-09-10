# mythicnode_gui_business.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta

# Core Modules
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
        self.title("MythicNode Defense Console")
        self.geometry("1200x700")
        self.configure(bg="#f4f4f4")

        # DPI-aware scaling
        self.tk.call('tk', 'scaling', 1.5)

        # Core modules
        self.ingest_monitor = IngestMonitor()
        self.codex = CodexEngine()
        self.personas = [Persona("ThreatHunter"), Persona("Compliance Auditor")]
        self.log = SymbolicLog()

        # Style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", font=("Segoe UI", 10))
        style.configure("TButton", font=("Segoe UI", 10))
        style.configure("TEntry", font=("Segoe UI", 10))
        style.configure("TFrame", background="#ffffff")

        # Layout
        self.create_dashboard()

    def create_dashboard(self):
        # Top Input Panel
        input_frame = ttk.Frame(self)
        input_frame.pack(fill="x", padx=20, pady=10)

        ttk.Label(input_frame, text="Live Data Input:").pack(side="left", padx=5)
        self.ingest_entry = ttk.Entry(input_frame, width=80)
        self.ingest_entry.pack(side="left", padx=5)
        ttk.Button(input_frame, text="Ingest", command=self.handle_ingest).pack(side="left", padx=5)

        # Main Panels
        main_frame = ttk.Frame(self)
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)

        left_panel = ttk.Frame(main_frame)
        left_panel.pack(side="left", fill="both", expand=True)

        right_panel = ttk.Frame(main_frame)
        right_panel.pack(side="right", fill="both", expand=True)

        # Threat Matrix
        ttk.Label(left_panel, text="Threat Matrix").pack(anchor="w")
        self.threat_list = tk.Listbox(left_panel, height=10, bg="#ffffff", fg="#333333", font=("Segoe UI", 10))
        self.threat_list.pack(fill="x", pady=5)

        # Codex Mutation Log
        ttk.Label(left_panel, text="Codex Mutation Log").pack(anchor="w")
        self.codex_log = tk.Text(left_panel, height=10, bg="#ffffff", fg="#333333", font=("Segoe UI", 10))
        self.codex_log.pack(fill="x", pady=5)

        # Persona Arcs
        ttk.Label(right_panel, text="Persona Arcs").pack(anchor="w")
        self.persona_log = tk.Text(right_panel, height=10, bg="#ffffff", fg="#333333", font=("Segoe UI", 10))
        self.persona_log.pack(fill="x", pady=5)

        # Symbolic Feedback
        ttk.Label(right_panel, text="Symbolic Feedback").pack(anchor="w")
        self.feedback_log = tk.Text(right_panel, height=10, bg="#ffffff", fg="#333333", font=("Segoe UI", 10))
        self.feedback_log.pack(fill="x", pady=5)

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

