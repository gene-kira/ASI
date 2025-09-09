# asi_core.py

import time
from vault import data_vault, log_feed
from symbolic_memory import record_event, link_persona
from trust_engine import calculate_trust_score, trust_scores
from trust_state import ALLOWLIST, BLOCKLIST, PERSONA

def add_to_allowlist(ip):
    ALLOWLIST.add(ip)
    log_feed.append(f"[FRONT DOOR] {ip} added to ALLOWLIST")
    trust_scores[ip] = 100

def add_to_blocklist(ip):
    BLOCKLIST.add(ip)
    for key in list(data_vault.keys()):
        if data_vault[key]["value"] == ip:
            del data_vault[key]
            log_feed.append(f"[BACK DOOR PURGE] {key} from {ip} deleted")
    log_feed.append(f"[BACK DOOR] {ip} added to BLOCKLIST")
    trust_scores[ip] = 0

def inject_deception_overlay(overlay_type):
    data_vault[f"overlay_{overlay_type}"] = {
        "value": f"deception_{overlay_type}",
        "timestamp": time.time(),
        "ttl": 60
    }
    log_feed.append(f"[OVERLAY INJECTED] {overlay_type}")

def mutate_persona(ip, trigger):
    current = PERSONA.get(ip, "observer")
    new_persona = {
        "deception": "ghost",
        "repeated_access": "mirror",
        "override": "trusted"
    }.get(trigger, current)
    PERSONA[ip] = new_persona
    link_persona(ip, new_persona)
    log_feed.append(f"[PERSONA MUTATED] {ip} → {new_persona}")

def asi_decision_engine(event_type, source_ip, payload_key):
    record_event(source_ip, event_type, payload_key)
    score = calculate_trust_score(source_ip)

    if score < 40 or source_ip in BLOCKLIST:
        add_to_blocklist(source_ip)
        log_feed.append(f"[ASI DECISION] {source_ip} score={score} → BLOCKED")
        data_vault.pop(payload_key, None)
        return "blocked"

    if source_ip not in ALLOWLIST:
        add_to_blocklist(source_ip)
        log_feed.append(f"[ASI DECISION] {source_ip} unknown → AUTO-BLOCKED")
        data_vault.pop(payload_key, None)
        return "auto-blocked"

    if "ASI" in source_ip or "ml" in payload_key.lower():
        inject_deception_overlay("ml_corrupt")
        mutate_persona(source_ip, "deception")
        log_feed.append(f"[ASI DECISION] {source_ip} → ML deception injected")
        return "deceived"

    mutate_persona(source_ip, "repeated_access")
    log_feed.append(f"[ASI DECISION] {source_ip} score={score} → ALLOWED")
    return "allowed"

