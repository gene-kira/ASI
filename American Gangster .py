import os, json, socket, threading, psutil
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string
from flask_socketio import SocketIO, emit

# 🔧 Initialize Flask + SocketIO
app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# 🧠 Core Data Structures
symbolic_registry = {}
swarm_nodes = set()
persona_clearance = {"admin": 10, "analyst": 5, "guest": 1}

# 🔍 Normal Traffic Baseline
normal_baseline = {
    "hours": list(range(8, 18)),  # 8 AM to 6 PM
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

# 🔮 Expected Persona Logic
def expected_personas_for_action(action):
    if action == "ingest": return {"admin", "analyst"}
    return {"admin"}

# 🔮 Gut Feeling Protocol
def gut_feeling_trigger(event):
    hour = datetime.fromisoformat(event["timestamp"]).hour
    if hour not in normal_baseline["hours"]: return True
    if event["country"] not in normal_baseline["countries"]: return True
    if event["protocol"] not in normal_baseline["protocols"]: return True
    if event["volume_kb"] > normal_baseline["avg_volume_kb"] * 2: return True
    if event["persona"] not in expected_personas_for_action(event["action"]): return True
    return False

# 🔥 No-Fear Autonomous Trigger
def no_fear_trigger(event):
    return gut_feeling_trigger(event)

# 🔥 Purge Ritual
def purge_data(data):
    print(f"[PURGE] Ritualized purge triggered for: {data}")
    socketio.emit("purge_event", {"data": data})

# 🧬 Ingest + Sync
def ingest_data(data, origin, persona):
    threat_level = classify_threat(data)
    purge_trigger = threat_level >= 7
    timestamp = datetime.utcnow().isoformat()
    event = {
        "origin": origin,
        "data": data,
        "threat_level": threat_level,
        "purge_trigger": purge_trigger,
        "persona": persona,
        "timestamp": timestamp,
        "country": origin,
        "protocol": "HTTPS",
        "volume_kb": len(data.encode()) // 1024,
        "action": "ingest"
    }
    symbolic_registry[timestamp] = event

    if no_fear_trigger(event):
        event["gut_triggered"] = True
        purge_data(data)
        socketio.emit("gut_event", event)
    else:
        socketio.emit("ingest_event", event)

    sync_to_swarm(data, threat_level)

# 🌐 Swarm Sync
def sync_to_swarm(data, threat_level):
    for node in swarm_nodes:
        try:
            sock = socket.socket()
            sock.connect((node, 8081))
            sock.send(json.dumps({
                "data": data,
                "threat_level": threat_level
            }).encode())
            sock.close()
        except:
            print(f"[SYNC FAIL] Node unreachable: {node}")

# 🖥️ GUI Dashboard
@app.route("/")
def dashboard():
    return render_template_string("""
    <!DOCTYPE html>
    <html>
    <head>
      <title>Codex Sentinel Dashboard</title>
      <script src="https://cdn.socket.io/4.5.4/socket.io.min.js"></script>
    </head>
    <body>
      <h1>🛡️ Codex Sentinel Dashboard</h1>
      <div id="events"></div>
      <script>
        const socket = io();
        const eventsDiv = document.getElementById("events");

        socket.on("ingest_event", data => {
          const entry = document.createElement("div");
          entry.innerHTML = `<b>Ingested:</b> ${data.data} | Threat: ${data.threat_level} | Origin: ${data.origin}`;
          eventsDiv.prepend(entry);
        });

        socket.on("gut_event", data => {
          const entry = document.createElement("div");
          entry.innerHTML = `<b style="color:red">NO-FEAR PURGE:</b> ${data.data} | Country: ${data.country} | Hour: ${new Date(data.timestamp).getHours()} | Volume: ${data.volume_kb} KB`;
          eventsDiv.prepend(entry);
        });

        socket.on("purge_event", data => {
          const entry = document.createElement("div");
          entry.innerHTML = `<b style="color:darkred">PURGED:</b> ${data.data}`;
          eventsDiv.prepend(entry);
        });
      </script>
    </body>
    </html>
    """)

# 🧠 API Endpoints
@app.route("/ingest", methods=["POST"])
def ingest():
    payload = request.json
    origin = payload.get("origin", "unknown")
    persona = payload.get("persona", "guest")
    data = payload.get("data", "")
    ingest_data(data, origin, persona)
    return jsonify({"status": "ingested"})

@app.route("/swarm/register", methods=["POST"])
def register_node():
    node_ip = request.json.get("ip")
    swarm_nodes.add(node_ip)
    return jsonify({"status": "registered", "nodes": list(swarm_nodes)})

@app.route("/defense/self_destruct", methods=["POST"])
def self_destruct():
    reason = request.json.get("reason", "unknown")
    symbolic_registry.clear()
    socketio.emit("purge_event", {"data": "ALL DATA PURGED", "reason": reason})
    return jsonify({"status": "purged", "reason": reason})

# 🚀 Launch Shell
if __name__ == "__main__":
    socketio.run(app, port=8080)

