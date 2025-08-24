import threading
import socket
import json

# 🧠 Trusted Node Registry
trusted_nodes = {
    "Node-A": "192.168.1.10",
    "Node-B": "192.168.1.11",
    "Node-C": "192.168.1.12"
}

SYNC_PORT = 5050
BUFFER_SIZE = 1024

# 🕸️ Real-Time Sync Listener
def listen_for_sync(mutation_output):
    def handler():
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
            s.bind(("", SYNC_PORT))
            while True:
                try:
                    data, addr = s.recvfrom(BUFFER_SIZE)
                    ip = addr[0]
                    if ip in trusted_nodes.values():
                        payload = json.loads(data.decode())
                        node_id = payload.get("node_id", "Unknown")
                        event = payload.get("event", "Sync")
                        msg = f"🕸️ Real sync from {node_id} ({ip}) — {event}\n"
                        mutation_output.insert("end", msg)
                        print(f"[Swarm Sync] {msg.strip()}")
                    else:
                        print(f"[Swarm Sync] Ignored untrusted node: {ip}")
                except Exception as e:
                    print(f"[Swarm Sync Error] {e}")
    threading.Thread(target=handler, daemon=True).start()

# 🧠 Start Real-Time Sync Engine
def start_swarm_sync(mutation_output):
    listen_for_sync(mutation_output)

