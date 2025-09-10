# mythicnode_autonomous_live_log.py

import tkinter as tk
from tkinter import ttk
from datetime import datetime, timedelta
import threading
import logging
import json
import os
import time

# Secure Log Stream Setup
logger = logging.getLogger("mythicnode")
handler = logging.FileHandler("mythicnode.log")
formatter = logging.Formatter('%(asctime)s %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.INFO)

def emit_log(event):
    payload = {
        "timestamp": datetime.utcnow().isoformat(),
        "event": event
    }
    logger.info(json.dumps(payload))

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
        if "backdoor" in data or "phantom" in data:
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
            mutation = f"{datetime.utcnow()}: Codex mutated due to ghost sync."
            self.mutations.append(mutation)
            emit_log(mutation)

class Persona:
    def __init__(self, name):
        self.name = name
        self.arc = []

    def narrate(self, event):
        entry = f"{datetime.utcnow()}: {self.name} - {event}"
        self.arc.append(entry)
        emit_log(entry)

class SymbolicLog:
    def __init__(self):
        self.entries = []

    def log(self, message):
        entry = f"{datetime.utcnow()}: {message}"
        self.entries.append(entry)
        emit_log(entry)
        return entry

class SwarmSync:
    def __init__(self):
        self.synced_nodes = []

    def sync(self, codex_rules):
        entry = f"{datetime.utcnow()}: Codex synced with swarm node."
        self.synced_nodes.append({
            "timestamp": datetime.utcnow(),
            "rules": codex_rules
        })
        emit_log(entry)
        return entry

# Auto-generate live system log
def start_live_log_writer(log_path):
    def write_loop():
        keywords = [
            "telemetry MAC:AA:BB:CC",
            "phantom backdoor signature",
            "ghost sync detected",
            "IP:192.168.1.1 telemetry",
            "backdoor ping from node-7",
            "MAC:DE:AD:BE:EF ghost sync"
        ]
        with open(log_path, "a") as f:
            while True:
                entry = f"{datetime.utcnow()} :: {keywords[int(time.time()) % len(keywords)]}\n"
                f.write(entry)
                f.flush()
                time.sleep(5)
    threading.Thread(target=write_loop, daemon=True).start()

# GUI Application
class MythicNodeGUI(tk.Tk):
    def __init__(self, log_path):
        super().__init__()
        self.title("MYTHICNODE AUTONOMOUS CONSOLE")
        self.geometry("800x450")
        self.configure(bg="#0f1114")
        self.tk.call('tk', 'scaling', 1.2)

        # Core modules
        self.ingest_monitor = IngestMonitor()
        self.codex = CodexEngine()
        self.personas = [Persona("ThreatHunter"), Persona("Compliance Auditor")]
        self.log = SymbolicLog()
        self.swarm_sync = SwarmSync()
        self.log_path = log_path

        # Style
        style = ttk.Style(self)
        style.theme_use("clam")
        style.configure("TLabel", font=("Consolas", 9), background="#1c1f24", foreground="#00ffcc")
        style.configure("TFrame", background="#1c1f24")

        # Layout
        self.create_panels()

        # Start log tailing
        threading.Thread(target=self.tail_log_file, daemon=True).start()

    def create_panels(self):
        frame = ttk.Frame(self)
        frame.pack(fill="both", expand=True, padx=10, pady=10)

        ttk.Label(frame, text="THREAT MATRIX").grid(row=0, column=0, sticky="w")
        self.threat_list = tk.Listbox(frame, height=6, bg="#1c1f24", fg="#ff6666", font=("Consolas", 9))
        self.threat_list.grid(row=1, column=0, sticky="ew")

        ttk.Label(frame, text="CODEX MUTATIONS").grid(row=2, column=0, sticky="w")
        self.codex_log = tk.Text(frame, height=6, bg="#1c1f24", fg="#00ffcc", font=("Consolas", 9))
        self.codex_log.grid(row=3, column=0, sticky="ew")

        ttk.Label(frame, text="PERSONA ARCS").grid(row=0, column=1, sticky="w")
        self.persona_log = tk.Text(frame, height=6, bg="#1c1f24", fg="#ccccff", font=("Consolas", 9))
        self.persona_log.grid(row=1, column=1, sticky="ew")

        ttk.Label(frame, text="SYMBOLIC FEEDBACK").grid(row=2, column=1, sticky="w")
        self.feedback_log = tk.Text(frame, height=6, bg="#1c1f24", fg="#ffffff", font=("Consolas", 9))
        self.feedback_log.grid(row=3, column=1, sticky="ew")

        frame.grid_columnconfigure(0, weight=1)
        frame.grid_columnconfigure(1, weight=1)

    def tail_log_file(self):
        with open(self.log_path, "r") as f:
            f.seek(0, os.SEEK_END)
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.5)
                    continue
                self.process_log_line(line.strip())

    def process_log_line(self, data):
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
            self.feedback_log.insert(tk.END, sync_status + "\n")
        else:
            feedback = self.log.log("No threat detected.")
            self.feedback_log.insert(tk.END, feedback + "\n")

# Run GUI with auto-generated live log
if __name__ == "__main__":
    log_file_path = "mythicnode_system.log"
    if not os.path.exists(log_file_path):
        open(log_file_path, "w").close()
    start_live_log_writer(log_file_path)
    app = MythicNodeGUI(log_file_path)
    app.mainloop()

