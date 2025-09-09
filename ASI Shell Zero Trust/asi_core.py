# asi_core.py

import time
from vault import data_vault, log_feed

# 🔐 Trust Lists
ALLOWLIST = set()
BLOCKLIST = set()

# ✅ Manual Controls
def add_to_allowlist(ip):
    ALLOWLIST.add(ip)
    log_feed.append(f"[FRONT DOOR] {ip} added to ALLOWLIST")

def add_to_blocklist(ip):
    BLOCKLIST.add(ip)
    for key in list(data_vault.keys()):
        if data_vault[key]["value"] == ip:
            del data_vault[key]
            log_feed.append(f"[BACK DOOR PURGE] {key} from {ip} deleted")
    log_feed.append(f"[BACK DOOR] {ip} added to BLOCKLIST")

# 🎭 Deception Overlay Injector
def inject_deception_overlay(overlay_type):
    if overlay_type == "ml_corrupt":
        data_vault["ML_dashboard"] = {
            "value": "corrupted weights",
            "timestamp": time.time(),
            "ttl": 60
        }
    elif overlay_type == "crypto_fake":
        data_vault["wallet_gui"] = {
            "value": "0xFAKE123",
            "timestamp": time.time(),
            "ttl": 45
        }
    log_feed.append(f"[OVERLAY INJECTED] {overlay_type}")

# 🧠 ASI Decision Engine
def asi_decision_engine(event_type, source_ip, payload_key):
    # 🔴 Blocked IP
    if source_ip in BLOCKLIST:
        log_feed.append(f"[ASI DECISION] {source_ip} already blocked — PURGE")
        data_vault.pop(payload_key, None)
        return "purged"

    # 🟡 Unknown IP → Auto-block
    if source_ip not in ALLOWLIST:
        BLOCKLIST.add(source_ip)
        log_feed.append(f"[ASI DECISION] {source_ip} unknown — AUTO-BLOCKED")
        data_vault.pop(payload_key, None)
        return "auto-blocked"

    # 🧬 ASI/ML Threat → Deceive
    if "ASI" in source_ip or "ml" in payload_key.lower():
        inject_deception_overlay("ml_corrupt")
        log_feed.append(f"[ASI DECISION] {source_ip} → ML deception injected")
        return "deceived"

    # 🟢 Trusted IP
    log_feed.append(f"[ASI DECISION] {source_ip} trusted — ALLOWED")
    return "allowed"

