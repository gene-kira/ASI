# 🛡️ Borg Network Guard Tactical Shell
# Author: killer666 + Copilot
# Purpose: Real-time autonomous defense swarm with GUI overlays, codex mutation, and persona injection

import subprocess, sys

# 🔧 Autoloader: Ensure required libraries
required_libs = ["tkinter", "socket", "threading", "json", "uuid", "datetime"]
for lib in required_libs:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# ✅ Imports
import socket, threading, time, json
from datetime import datetime
from uuid import uuid4
import tkinter as tk
from tkinter import ttk

# 🧬 CONFIGURATION
NODE_ID = str(uuid4())
NODE_ROLE = "Sentinel"
ALLOWED_COUNTRIES = ["US", "CA", "UK"]
CODEX_RETENTION = 3600
SYNC_PORT = 9090
SYNC_NODES = ["192.168.1.10", "192.168.1.11"]
threat_db = {}

# 📜 SYMBOLIC FEEDBACK
def narrate(event, detail):
    log = f"[{datetime.now()}] 🜂 {event}: {detail}"
    print(log)
    try:
        gui.update_threats(log) if "Threat" in event else None
        gui.log_sync(log) if "Sync" in event or "Codex" in event else None
    except:
        pass

# 🔍 LIVE DATA INGESTION
def ingest_packet(packet):
    origin = packet.get("origin", "unknown")
    threat_type = classify_threat(packet)
    if threat_type:
        threat_id = str(uuid4())
        threat_db[threat_id] = {
            "timestamp": time.time(),
            "type": threat_type,
            "origin": origin,
            "data": packet
        }
        narrate("Threat Ingested", f"{threat_type} from {origin}")
        if origin not in ALLOWED_COUNTRIES:
            trigger_lockdown(threat_id)

# 🧠 THREAT CLASSIFICATION
def classify_threat(packet):
    if "backdoor" in packet.get("signature", ""):
        return "Backdoor"
    if "ghost_sync" in packet.get("flags", []):
        mutate_codex("phantom_node")
        return "Ghost Sync"
    if packet.get("mac") == "00:00:00:00:00:00":
        return "MAC Spoof"
    return None

# 🔥 PURGE LOGIC
def purge_threats():
    now = time.time()
    for tid in list(threat_db.keys()):
        if now - threat_db[tid]["timestamp"] > CODEX_RETENTION:
            narrate("Threat Purged", f"{threat_db[tid]['type']} from {threat_db[tid]['origin']}")
            del threat_db[tid]

# 🧬 CODEX MUTATION
def mutate_codex(trigger):
    global CODEX_RETENTION
    if trigger == "phantom_node":
        CODEX_RETENTION = max(600, CODEX_RETENTION // 2)
        narrate("Codex Mutated", "Retention shortened due to ghost sync")
        gui.update_codex(CODEX_RETENTION)
        sync_codex()

# 🕸️ REAL NODE SYNC
def sync_codex():
    codex_payload = json.dumps({
        "node_id": NODE_ID,
        "retention": CODEX_RETENTION,
        "timestamp": time.time()
    })
    for node in SYNC_NODES:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((node, SYNC_PORT))
                s.sendall(codex_payload.encode())
                narrate("Codex Sync", f"Sent to {node}")
        except Exception as e:
            narrate("Sync Failed", f"{node}: {e}")

# 🎭 PERSONA INJECTION
def inject_persona(persona_type):
    persona = {
        "ThreatHunter": "Aggressive scan bait deployed",
        "ComplianceAuditor": "Passive observer activated"
    }.get(persona_type, "Unknown persona")
    narrate("Persona Injected", f"{persona_type}: {persona}")
    gui.update_persona(persona_type)

# 🌐 COUNTRY FILTERING
def trigger_lockdown(threat_id):
    origin = threat_db[threat_id]["origin"]
    narrate("Lockdown Triggered", f"Unauthorized origin: {origin}")
    inject_persona("ThreatHunter")

# 🧭 SYNC LISTENER
def sync_listener():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(("", SYNC_PORT))
    server.listen()
    narrate("Swarm Ready", f"Listening on port {SYNC_PORT}")
    while True:
        conn, addr = server.accept()
        data = conn.recv(1024)
        if data:
            payload = json.loads(data.decode())
            narrate("Codex Received", f"From {payload['node_id']} with retention {payload['retention']}")
            gui.update_codex(payload["retention"])

# 🖥️ GUI CLASS
class BorgTacticalGUI:
    def __init__(self, root):
        root.title("🛡️ Borg Network Guard Tactical Display")
        root.geometry("1000x600")
        root.configure(bg="#0f0f0f")

        self.threat_frame = ttk.LabelFrame(root, text="🧬 Threat Glyphs", padding=10)
        self.threat_frame.pack(fill="both", expand=True, side="left")
        self.threat_list = tk.Listbox(self.threat_frame, bg="#1a1a1a", fg="#ff4444")
        self.threat_list.pack(fill="both", expand=True)

        self.codex_frame = ttk.LabelFrame(root, text="📜 Codex Mutation", padding=10)
        self.codex_frame.pack(fill="both", expand=True, side="top")
        self.codex_label = tk.Label(self.codex_frame, text="Retention: 3600s", fg="#00ff88", bg="#0f0f0f")
        self.codex_label.pack()

        self.persona_frame = ttk.LabelFrame(root, text="🎭 Persona Theater", padding=10)
        self.persona_frame.pack(fill="both", expand=True, side="top")
        self.persona_label = tk.Label(self.persona_frame, text="Active: None", fg="#ffaa00", bg="#0f0f0f")
        self.persona_label.pack()

        self.sync_frame = ttk.LabelFrame(root, text="🕸️ Swarm Sync Status", padding=10)
        self.sync_frame.pack(fill="both", expand=True, side="bottom")
        self.sync_log = tk.Text(self.sync_frame, height=10, bg="#1a1a1a", fg="#00ffff")
        self.sync_log.pack(fill="both", expand=True)

    def update_threats(self, threat_text):
        self.threat_list.insert(tk.END, threat_text)

    def update_codex(self, retention):
        self.codex_label.config(text=f"Retention: {retention}s")

    def update_persona(self, persona_name):
        self.persona_label.config(text=f"Active: {persona_name}")

    def log_sync(self, message):
        self.sync_log.insert(tk.END, f"{message}\n")
        self.sync_log.see(tk.END)

# 🚀 MAIN LOOP
def main_loop():
    threading.Thread(target=sync_listener, daemon=True).start()
    while True:
        sample_packet = {
            "origin": "RU",
            "signature": "backdoor",
            "mac": "00:00:00:00:00:00",
            "flags": ["ghost_sync"]
        }
        ingest_packet(sample_packet)
        purge_threats()
        time.sleep(5)

# 🌀 LAUNCH
if __name__ == "__main__":
    root = tk.Tk()
    gui = BorgTacticalGUI(root)
    threading.Thread(target=main_loop, daemon=True).start()
    narrate("Node Activated", f"{NODE_ROLE} [{NODE_ID}]")
    root.mainloop()

