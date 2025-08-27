# memory.py

import json, os, time

MEMORY_FILE = "memory_vault.json"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

def update_memory(pulse, memory):
    memory[pulse.source] = {
        "fusion_signature": f"F:{hash(pulse.source + str(pulse.entropy)) % 9999}",
        "entropy_profile": memory.get(pulse.source, {}).get("entropy_profile", []) + [pulse.entropy],
        "lineage": [pulse.source, "core", "vault"],
        "last_seen": time.strftime("%Y-%m-%dT%H:%M:%S")
    }
    save_memory(memory)

def is_known_game(pulse, memory):
    return pulse.source in memory

def recall_optimization(pulse, memory):
    entry = memory.get(pulse.source)
    if entry:
        return f"[🧠 Recall] Fusion: {entry['fusion_signature']} | Lineage: {entry['lineage']}"
    return None

def detect_mutation_spike(entropy_profile):
    if len(entropy_profile) < 3:
        return False
    return max(entropy_profile) - min(entropy_profile) > 2.0

