from audit_scroll import log_event

def calculate_trust(entity):
    score = 100
    if entity.get("type") in ["unknown", "external", "rogue"]:
        score -= 80
    if entity.get("behavior") == "suspicious":
        score -= 30
    return max(score, 0)

def verify_entity(entity):
    trust_score = calculate_trust(entity)
    if trust_score < 50:
        quarantine(entity)
    else:
        log_event(f"Entity verified: {entity['id']} (Trust: {trust_score})")

def quarantine(entity):
    log_event(f"Entity quarantined: {entity['id']}")
    print(f"[ZeroTrust] 🚫 Quarantined: {entity['id']}")

