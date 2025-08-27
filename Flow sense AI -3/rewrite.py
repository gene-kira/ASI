# rewrite.py

import json, os, time
from random import randint, choice

CODEX_FILE = "fusion_codex.json"

def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    avg_entropy = sum(p.entropy for p in recent) / len(recent)
    variance = max(p.entropy for p in recent) - min(p.entropy for p in recent)
    return variance > 2.5 and avg_entropy > 7.0

def initiate_mutation_vote(pulse):
    votes = [choice(["yes", "no"]) for _ in range(5)]
    return votes.count("yes") >= 3

def rewrite_optimization_logic():
    new_threshold = randint(6, 8)
    print(f"[🧠 Rewrite] New cloaking threshold: {new_threshold}")
    return {
        "logic": f"entropy > {new_threshold}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": "symbolic_density_spike",
        "consensus": "mutation_vote_passed"
    }

def store_rewrite_codex(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

