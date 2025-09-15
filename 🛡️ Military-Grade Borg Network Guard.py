# 🛡️ Military-Grade Borg Network Guard
# Author: killer666 + Copilot
# Purpose: Real-time autonomous defense swarm with codex mutation, persona injection, and symbolic feedback

import socket, threading, time, json, os
from datetime import datetime
from uuid import uuid4

# 🧬 CONFIGURATION
NODE_ID = str(uuid4())
NODE_ROLE = "Sentinel"  # Options: Sentinel, Codex, Persona, Guardian
ALLOWED_COUNTRIES = ["US", "CA", "UK"]
CODEX_RETENTION = 3600  # seconds
SYNC_PORT = 9090
SYNC_NODES = ["192.168.1.10", "192.168.1.11"]  # Real nodes only

# 🧠 THREAT DATABASE
threat_db = {}

# 📜 SYMBOLIC FEEDBACK
def narrate(event, detail):
    print(f"[{datetime.now()}] 🜂 {event}: {detail}")

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

# 🌐 COUNTRY FILTERING
def trigger_lockdown(threat_id):
    origin = threat_db[threat_id]["origin"]
    narrate("Lockdown Triggered", f"Unauthorized origin: {origin}")
    inject_persona("ThreatHunter")

# 🧭 SERVER LISTENER FOR SYNC
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

# 🌀 MAIN LOOP
def main_loop():
    threading.Thread(target=sync_listener, daemon=True).start()
    while True:
        # Simulate live packet ingestion (replace with real packet capture)
        sample_packet = {
            "origin": "RU",
            "signature": "backdoor",
            "mac": "00:00:00:00:00:00",
            "flags": ["ghost_sync"]
        }
        ingest_packet(sample_packet)
        purge_threats()
        time.sleep(5)

# 🚀 LAUNCH
if __name__ == "__main__":
    narrate("Node Activated", f"{NODE_ROLE} [{NODE_ID}]")
    main_loop()

