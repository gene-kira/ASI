# trust_engine.py

from trust_state import ALLOWLIST, BLOCKLIST
trust_scores = {}

def calculate_trust_score(ip):
    score = trust_scores.get(ip, 50)
    if ip in ALLOWLIST:
        score += 30
    if ip in BLOCKLIST:
        score -= 50
    trust_scores[ip] = max(0, min(100, score))
    return trust_scores[ip]

def override_trust(ip, level):
    trust_scores[ip] = max(0, min(100, level))

