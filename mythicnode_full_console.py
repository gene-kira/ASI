# mythicnode_full_console.py

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

class CountryFilter:
    def __init__(self):
        self.allowed = {"US", "UK", "CA"}

    def is_allowed(self, origin):
        return origin in self.allowed

    def update_allowed(self, country_code):
        self.allowed.add(country_code)

class SwarmSync:
    def __init__(self):
        self.synced_nodes = []

    def sync(self, codex_rules):
        self.synced_nodes.append({
            "timestamp": datetime.utcnow(),
            "rules": codex_rules
        })
        return f"{datetime.utcnow()}: Codex synced with swarm node."

# GUI Application
class MythicNodeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("MYTHICNODE COMMAND CONSOLE")
        self.geometry("1600x900")
        self.configure(bg="#0f1114")
        self.tk.call('tk', 'scaling', 1.5)

        # Core modules
        self.ingest_monitor = IngestMonitor()
        self.codex = CodexEngine()
        self.personas = [Persona("ThreatHunter"), Persona("Compliance Auditor")]
        self.log = SymbolicLog()
        self.country_filter = CountryFilter()
        self.swarm_sync = SwarmSync()

        # Style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", font=("Consolas", 10), background="#1c1f24", foreground="#00ffcc")
        style.configure("TButton", font=("Consolas", 10), background="#2e3239", foreground="#ffffff")
        style.configure("TEntry", font=("Consolas", 10))
        style.configure("TFrame", background="#1c1f24")

        # Layout
        self.create_console()

    def create_console(self):
        # Input Panel
        input_frame = ttk.Frame(self)
        input_frame.grid(row=0, column=0, columnspan=3, sticky="ew", padx=20, pady=10)

        ttk.Label(input_frame, text=">> LIVE INGEST INPUT").grid(row=0, column=0, sticky="w")
        self.ingest_entry = ttk.Entry(input_frame, width=100)
        self.ingest_entry.grid(row=0, column=1, padx=10)
        ttk.Button(input_frame, text="INGEST", command=self.handle_ingest).grid(row=0, column=2)

        # Country Filter Panel
        ttk.Label(input_frame, text=">> ORIGIN COUNTRY").grid(row=1, column=0, sticky="w")
        self.origin_entry = ttk.Entry(input_frame, width=20)
        self.origin_entry.grid(row=1, column=1, sticky="w")
        ttk.Button(input_frame, text="ALLOW", command=self.allow_country).grid(row=1, column=2)

        # Left Column
        left_frame = ttk.Frame(self)
        left_frame.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)

        ttk.Label(left_frame, text="THREAT MATRIX").pack(anchor="w")
        self.threat_list = tk.Listbox(left_frame, height=12, bg="#1c1f24", fg="#ff6666", font=("Consolas", 10))
        self.threat_list.pack(fill="x", pady=5)

        ttk.Label(left_frame, text="CODEX MUTATION LOG").pack(anchor="w")
        self.codex_log = tk.Text(left_frame, height=12, bg="#1c1f24", fg="#00ffcc", font=("Consolas", 10))
        self.codex_log.pack(fill="x", pady=5)

        # Center Column
        center_frame = ttk.Frame(self)
        center_frame.grid(row=1, column=1, sticky="nsew", padx=20, pady=10)

        ttk.Label(center_frame, text="PERSONA ARC TRACKER").pack(anchor="w")
        self.persona_log = tk.Text(center_frame, height=12, bg="#1c1f24", fg="#ccccff", font=("Consolas", 10))
        self.persona_log.pack(fill="x", pady=5)

        ttk.Label(center_frame, text="SWARM SYNC STATUS").pack(anchor="w")
        self.sync_log = tk.Text(center_frame, height=12, bg="#1c1f24", fg="#66ffcc", font=("Consolas", 10))
        self.sync_log.pack(fill="x", pady=5)

        # Right Column
        right_frame = ttk.Frame(self)
        right_frame.grid(row=1, column=2, sticky="nsew", padx=20, pady=10)

        ttk.Label(right_frame, text="SYMBOLIC FEEDBACK CHANNEL").pack(anchor="w")
        self.feedback_log = tk.Text(right_frame, height=25, bg="#1c1f24", fg="#ffffff", font=("Consolas", 10))
        self.feedback_log.pack(fill="both", expand=True)

        # Grid weight
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)

    def handle_ingest(self):
        data = self.ingest_entry.get()
        origin = self.origin_entry.get().strip().upper()
        if not self.country_filter.is_allowed(origin):
            blocked = self.log.log(f"Blocked data from origin: {origin}")
            self.feedback_log.insert(tk.END, blocked + "\n")
            return

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
            sync_status = self.swarm_sync.sync(self.codex.retention)
            self.sync_log.insert(tk.END, sync_status + "\n")
        else:
            feedback = self.log.log("No threat detected.")
            self.feedback_log.insert(tk.END, feedback + "\n")

    def allow_country(self):
        code = self.origin_entry.get().strip().upper()
        self.country_filter.update_allowed(code)
        self.feedback_log.insert(tk.END, f"{datetime.utcnow()}: Country allowed: {code}\n")

# Run GUI
if __name__ == "__main__":
    app = MythicNodeGUI()
    app.mainloop()

