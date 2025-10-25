# 🔄 Autoloader Ritual
import subprocess, sys
required_packages = ["flask", "flask_socketio", "psutil", "requests"]
def install_and_import(pkg): 
    try: __import__(pkg if pkg != "flask_socketio" else "flask_socketio")
    except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
for pkg in required_packages: install_and_import(pkg)

# 🔧 Core Imports
import os, json, socket, threading, psutil, random
from datetime import datetime
import tkinter as tk
from tkinter import scrolledtext
from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit
import queue

# 🔧 Flask + SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")
event_queue = queue.Queue()

# 🧠 Core Data
symbolic_registry = {}
swarm_nodes = set()
anomaly_clusters = {}
persona_clearance = {"admin": 10, "analyst": 5, "guest": 1}
normal_baseline = {
    "hours": list(range(8, 18)),
    "countries": {"US", "CA"},
    "protocols": {"HTTPS", "DNS"},
    "avg_volume_kb": 500
}

# 🔍 Threat Classification
def classify_threat(data):
    score = 0
    if "exec" in data or "rm -rf" in data: score += 5
    if "http://" in data or "ftp://" in data: score += 2
    if "password" in data: score += 3
    return score

# 🔐 Encrypted Traffic Detection
def detect_encrypted_anomaly(flow):
    entropy = flow.get("entropy", random.uniform(6.5, 8.5))
    tls_version = flow.get("tls_version", "TLS 1.1")
    if entropy > 7.5 or tls_version not in {"TLS 1.2", "TLS 1.3"}:
        return True
    return False

# 👤 Persona Audit Overlay
def expected_personas_for_action(action):
    return {"admin", "analyst"} if action == "ingest" else {"admin"}

def audit_persona_action(persona, action):
    return persona in expected_personas_for_action(action)

# 🔮 Gut Feeling Protocol
def gut_feeling_trigger(event):
    hour = datetime.fromisoformat(event["timestamp"]).hour
    return (
        hour not in normal_baseline["hours"] or
        event["country"] not in normal_baseline["countries"] or
        event["protocol"] not in normal_baseline["protocols"] or
        event["volume_kb"] > normal_baseline["avg_volume_kb"] * 2 or
        not audit_persona_action(event["persona"], event["action"])
    )

# 🔥 No-Fear Autonomous Trigger
def no_fear_trigger(event):
    return gut_feeling_trigger(event) or detect_encrypted_anomaly(event)

# 🐝 Swarm-Wide Anomaly Clustering
def sync_anomaly_cluster(event):
    cluster_id = hash((event["origin"], event["threat_level"], event["timestamp"][:13]))
    anomaly_clusters.setdefault(cluster_id, []).append(event)
    if len(anomaly_clusters[cluster_id]) >= 3:
        purge_data(f"Cluster {cluster_id} triggered purge")
        event_queue.put(("CLUSTER", f"Swarm consensus purge: Cluster {cluster_id}"))

# 🔥 Purge Ritual
def purge_data(data):
    event_queue.put(("PURGE", f"Ritualized purge triggered for: {data}"))

# 🧬 Ingest + Sync
def ingest_data(data, origin, persona):
    threat_level = classify_threat(data)
    timestamp = datetime.utcnow().isoformat()
    event = {
        "origin": origin,
        "data": data,
        "threat_level": threat_level,
        "persona": persona,
        "timestamp": timestamp,
        "country": origin,
        "protocol": "HTTPS",
        "volume_kb": len(data.encode()) // 1024,
        "action": "ingest",
        "entropy": random.uniform(6.5, 8.5),
        "tls_version": random.choice(["TLS 1.1", "TLS 1.2", "TLS 1.3"])
    }
    symbolic_registry[timestamp] = event

    if no_fear_trigger(event):
        purge_data(data)
        event_queue.put(("GUT", f"NO-FEAR PURGE: {data} | Country: {event['country']} | Hour: {datetime.fromisoformat(timestamp).hour} | Volume: {event['volume_kb']} KB"))
    else:
        event_queue.put(("INGEST", f"Ingested: {data} | Threat: {threat_level} | Origin: {origin}"))

    sync_to_swarm(data, threat_level)
    sync_anomaly_cluster(event)

def sync_to_swarm(data, threat_level):
    for node in swarm_nodes:
        try:
            sock = socket.socket()
            sock.connect((node, 8081))
            sock.send(json.dumps({"data": data, "threat_level": threat_level}).encode())
            sock.close()
        except:
            event_queue.put(("ERROR", f"SYNC FAIL: Node unreachable {node}"))

# 🧠 Flask API
@app.route("/ingest", methods=["POST"])
def api_ingest():
    payload = request.json
    ingest_data(payload.get("data", ""), payload.get("origin", "unknown"), payload.get("persona", "guest"))
    return jsonify({"status": "ingested"})

@app.route("/swarm/register", methods=["POST"])
def api_register_node():
    node_ip = request.json.get("ip")
    swarm_nodes.add(node_ip)
    return jsonify({"status": "registered", "nodes": list(swarm_nodes)})

@app.route("/defense/self_destruct", methods=["POST"])
def api_self_destruct():
    symbolic_registry.clear()
    event_queue.put(("PURGE", "ALL DATA PURGED"))
    return jsonify({"status": "purged", "reason": "manual trigger"})

# 🖥️ MagicBox GUI
def launch_gui():
    root = tk.Tk()
    root.title("🧙 Codex Sentinel — Mythic Precision Edition")
    root.geometry("750x550")
    root.configure(bg="#1e1e2f")

    log = scrolledtext.ScrolledText(root, bg="#2e2e3f", fg="white", font=("Consolas", 10), wrap=tk.WORD)
    log.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

    def push_test_ingest():
        ingest_data("exec rm -rf /", "RU", "guest")

    def update_log():
        while not event_queue.empty():
            kind, msg = event_queue.get()
            color = {"INGEST": "white", "GUT": "red", "PURGE": "darkred", "ERROR": "orange", "CLUSTER": "magenta"}.get(kind, "gray")
            log.insert(tk.END, f"{msg}\n", kind)
            log.tag_config(kind, foreground=color)
            log.see(tk.END)
        root.after(500, update_log)

    btn = tk.Button(root, text="Trigger Test Ingest", command=push_test_ingest, bg="#3e3e5f", fg="white", font=("Consolas", 10))
    btn.pack(pady=5)

    update_log()
    threading.Thread(target=lambda: socketio.run(app, port=8080), daemon=True).start()
    root.mainloop()

# 🚀 Launch Everything
if __name__ == "__main__":
    launch_gui()

