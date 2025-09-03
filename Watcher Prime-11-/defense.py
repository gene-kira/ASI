# defense.py — Zero-Trust Threat Monitor
from codex import trigger_self_destruct, log_output

def monitor_data(data_packet):
    if data_packet["channel"] == "backdoor":
        trigger_self_destruct(data_packet["id"], 3)
        log_output(f"[🛡️] Backdoor detected — auto-destruct in 3s")

    elif data_packet.get("mac") or data_packet.get("ip"):
        trigger_self_destruct(data_packet["id"], 30)
        log_output(f"[🛡️] MAC/IP exposure — auto-destruct in 30s")

    elif data_packet["type"] == "personal":
        trigger_self_destruct(data_packet["id"], 86400)
        log_output(f"[🛡️] Personal data flagged — auto-destruct in 1 day")

    elif data_packet["type"] == "fake_telemetry":
        trigger_self_destruct(data_packet["id"], 30)
        log_output(f"[🛡️] Fake telemetry injected — auto-destruct in 30s")

