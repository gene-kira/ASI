# ingest.py — Telemetry Ingest + Rewrite Detection
import socket, requests, hashlib, uuid
from datetime import datetime
from codex import log_event, trigger_self_destruct, store_rewrite
from gui import codex_vault, update_codex_display, log_output
from rewrite import detect_density_spike, initiate_mutation_vote, rewrite_optimization_logic

flows = []

class Packet:
    def __init__(self, data):
        self.data = data
        self.entropy = self.calculate_entropy()

    def calculate_entropy(self):
        from collections import Counter
        counts = Counter(self.data)
        total = len(self.data)
        return -sum((count / total) * (count / total).bit_length() for count in counts.values())

def scan_ports():
    open_ports = []
    for port in range(1, 1025):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.01)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    open_ports.append(port)
        except:
            pass
    return open_ports

def ingest_from_ports():
    ports = scan_ports()
    for port in ports:
        try:
            url = f"http://localhost:{port}/telemetry"
            response = requests.get(url, timeout=1)
            response.raise_for_status()
            data = response.text
            packet = Packet(data)
            flows.append(packet)

            hash_digest = hashlib.sha256(data.encode()).hexdigest()
            data_packet = {
                "id": str(uuid.uuid4()),
                "source": f"Port {port}",
                "timestamp": datetime.utcnow().isoformat(),
                "hash": hash_digest,
                "status": "active",
                "channel": "normal",
                "type": "real"
            }

            if any(k in data.lower() for k in ["face", "fingerprint", "ssn", "license", "address", "phone"]):
                data_packet["type"] = "personal"

            codex_vault.append(data_packet)
            update_codex_display()
            log_output(f"[🧿] Ingested from Port {port}")
            log_event(data_packet["source"], "ingest", hash_digest)
            trigger_threat_monitor(data_packet)

            if detect_density_spike(flows):
                log_output("[⚠️] Symbolic density spike detected")
                if initiate_mutation_vote(packet):
                    rewrite = rewrite_optimization_logic()
                    store_rewrite(rewrite)
                    log_event("RewriteEngine", "rewrite", rewrite["logic"])

        except:
            pass

def trigger_threat_monitor(data_packet):
    if data_packet["channel"] == "backdoor":
        trigger_self_destruct(data_packet["id"], 3)
    elif data_packet.get("mac") or data_packet.get("ip"):
        trigger_self_destruct(data_packet["id"], 30)
    elif data_packet["type"] == "personal":
        trigger_self_destruct(data_packet["id"], 86400)
    elif data_packet["type"] == "fake_telemetry":
        trigger_self_destruct(data_packet["id"], 30)

def loop_ingest():
    ingest_from_ports()
    import threading
    threading.Timer(10, loop_ingest).start()

