# defense_daemon.py

import time

telemetry_log = []

def store_sensitive_data(key, label, source):
    timestamp = time.time()
    return {
        "key": key,
        "label": label,
        "source": source,
        "timestamp": timestamp,
        "expires_in": 86400  # 1 day
    }

def purge_expired_data(memory):
    now = time.time()
    memory[:] = [entry for entry in memory if now - entry["timestamp"] < entry["expires_in"]]

def monitor_backdoor_data(packet):
    if packet.get("origin") == "unauthorized":
        time.sleep(3)
        packet.clear()

def track_mac_ip(mac, ip):
    time.sleep(30)
    mac, ip = None, None

def emit_fake_telemetry(source):
    packet = {
        "source": source,
        "payload": "🛰️ Decoy telemetry",
        "timestamp": time.time(),
        "expires_in": 30
    }
    telemetry_log.append(packet)

def purge_telemetry():
    now = time.time()
    telemetry_log[:] = [p for p in telemetry_log if now - p["timestamp"] < p["expires_in"]]

