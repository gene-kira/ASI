import requests, hashlib, uuid, time, threading
from datetime import datetime

# Trusted telemetry endpoints
TELEMETRY_SOURCES = {
    "sensor_alpha": "http://localhost:5000/alpha",
    "sensor_beta": "http://localhost:5000/beta",
    "external_feed": "https://api.example.com/livefeed"
}

# Codex Vault
codex_vault = []

# Replicator Registry
replicator_nodes = []

# Self-destruct timers
def self_destruct(data_id, delay_sec):
    def destroy():
        print(f"[DEFENSE] 💥 Data {data_id} self-destructed after {delay_sec}s")
        # Purge from vault, memory, etc.
        for entry in codex_vault:
            if entry["entry_id"] == data_id:
                entry["status"] = "destroyed"
    threading.Timer(delay_sec, destroy).start()

# Codex Vault logger
def log_codex_event(source, event_type, overlay, resonance, trail, destruct_timer):
    entry = {
        "entry_id": str(uuid.uuid4()),
        "timestamp": datetime.utcnow().isoformat(),
        "source": source,
        "event_type": event_type,
        "symbolic_overlay": overlay,
        "emotional_resonance": resonance,
        "mutation_trail": trail,
        "destruct_timer": destruct_timer,
        "status": "active"
    }
    codex_vault.append(entry)
    print(f"[Codex] 📜 Logged {event_type} from {source} with overlay {overlay}")
    if destruct_timer > 0:
        self_destruct(entry["entry_id"], destruct_timer)

# Integrity check
def verify_integrity(data):
    return hashlib.sha256(data.encode()).hexdigest()

# Swarm sync pulse
def sync_pulse(node_id, hash_digest):
    print(f"[Swarm] 🔁 Sync pulse from {node_id} with hash {hash_digest[:10]}")
    log_codex_event(
        source=node_id,
        event_type="sync",
        overlay="glyph_sync",
        resonance="mythic",
        trail=[hash_digest],
        destruct_timer=0
    )

# Replicator logic
def replicate_daemon(node_name):
    print(f"[Replicator] 🧬 Spawning clone: {node_name}")
    replicator_nodes.append(node_name)
    log_codex_event(
        source=node_name,
        event_type="replication",
        overlay="glyph_clone",
        resonance="curiosity",
        trail=[],
        destruct_timer=0
    )

# Outbound monitor
def outbound_monitor(data_packet):
    if data_packet["channel"] == "backdoor":
        self_destruct(data_packet["id"], 3)
    elif data_packet.get("mac") or data_packet.get("ip"):
        self_destruct(data_packet["id"], 30)
    elif data_packet["type"] == "personal":
        self_destruct(data_packet["id"], 86400)
    elif data_packet["type"] == "fake_telemetry":
        self_destruct(data_packet["id"], 30)

# Ingest loop
def ingest_telemetry():
    for source, url in TELEMETRY_SOURCES.items():
        try:
            response = requests.get(url, timeout=2)
            response.raise_for_status()
            raw_data = response.text
            timestamp = datetime.utcnow().isoformat()
            integrity_hash = verify_integrity(raw_data)

            data_packet = {
                "id": str(uuid.uuid4()),
                "source": source,
                "timestamp": timestamp,
                "hash": integrity_hash,
                "data": raw_data,
                "channel": "normal",
                "type": "real"
            }

            log_codex_event(
                source=source,
                event_type="ingest",
                overlay="glyph_ingest",
                resonance="alert",
                trail=[integrity_hash],
                destruct_timer=0
            )

            sync_pulse(source, integrity_hash)
            outbound_monitor(data_packet)

        except Exception as e:
            print(f"[Watcher] ❌ Failed to ingest from {source}: {e}")

# Daemon loop
def daemon_loop():
    print("[Daemon] 🚀 Watcher Prime activated")
    replicate_daemon("Watcher_Clone_A")
    replicate_daemon("Watcher_Clone_B")
    while True:
        ingest_telemetry()
        time.sleep(5)

# Launch daemon
if __name__ == "__main__":
    daemon_loop()

