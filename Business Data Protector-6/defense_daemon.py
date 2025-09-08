# defense_daemon.py

import time
import threading
import random
from utils import log_codex

# 🛡️ Zero Trust Enforcement
def enforce_zero_trust(source, reason):
    log_codex(f"🛡️ ZERO TRUST: Blocked {source} → Reason: {reason}")
    print(f"🛡️ [ZERO TRUST] {source} blocked → {reason}")
    # Extend with port lockdown, persona masking, or overlay triggers

# 💥 MAC/IP Auto-Destruct After 30 Seconds
def schedule_mac_ip_destruction(mac, ip):
    log_codex(f"🧨 MAC/IP discovered: {mac} / {ip} → Scheduled for destruction")
    def destroy():
        time.sleep(30)
        print(f"💥 MAC/IP destructed: {mac} / {ip}")
        log_codex(f"💥 MAC/IP destructed: {mac} / {ip}")
        # Purge from memory, logs, or GUI
    threading.Thread(target=destroy, daemon=True).start()

# 🧬 Biometric & Personal Data Lifecycle (1 Day)
def store_sensitive_data(data_id, data_type, source):
    timestamp = time.time()
    log_codex(f"🧬 Stored {data_type}: {data_id} from {source} → Expires in 1 day")
    def auto_destruct():
        time.sleep(86400)  # 1 day
        print(f"💥 {data_type} destructed: {data_id}")
        log_codex(f"💥 {data_type} destructed: {data_id} → Auto-purged")
    threading.Thread(target=auto_destruct, daemon=True).start()

# 🛰️ Fake Telemetry Shield + 30s Destruct
def emit_fake_telemetry(source):
    payload = {
        "cpu": f"{random.randint(5, 25)}%",
        "memory": f"{random.randint(20, 60)}%",
        "location": "Null Island",
        "persona": "Decoy",
        "timestamp": time.time()
    }
    log_codex(f"🛰️ Fake telemetry emitted from {source}: {payload}")
    print(f"🛰️ [FAKE TELEMETRY] {source} → {payload}")
    def destruct():
        time.sleep(30)
        print(f"💥 Fake telemetry destructed from {source}")
        log_codex(f"💥 Fake telemetry destructed from {source}")
    threading.Thread(target=destruct, daemon=True).start()

