# utils.py

import json
import os
import time
from datetime import datetime

MEMORY_FILE = "memory.json"
CODEX_FILE = "codex.log"

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {
        "allowed": [],
        "blocked": [],
        "countries_blocked": []
    }

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2)

def log_codex(message):
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    entry = f"[{timestamp}] {message}"
    try:
        with open(CODEX_FILE, "a", encoding="utf-8") as f:
            f.write(entry + "\n")
    except UnicodeEncodeError:
        safe_entry = entry.encode("ascii", errors="replace").decode("ascii")
        with open(CODEX_FILE, "a", encoding="utf-8") as f:
            f.write(safe_entry + "\n")
    print(entry)

def rewrite_optimization_logic():
    logic = f"Rewrite triggered @ {datetime.now().isoformat()}"
    return {
        "logic": logic,
        "timestamp": time.time()
    }

def store_rewrite_codex(rewrite):
    log_codex(f"📜 Rewrite logic: {rewrite['logic']}")

def vortex_pulse():
    import random
    return [random.randint(0, 100) for _ in range(10)]

def detect_density_spike(pulse):
    avg = sum(pulse) / len(pulse)
    spike = any(p > avg * 1.5 for p in pulse)
    log_codex(f"🌀 Entropy pulse: {pulse} | Spike: {spike}")
    return spike

def initiate_mutation_vote():
    import random
    vote = random.choice([True, False])
    log_codex(f"🗳️ Mutation vote result: {vote}")
    return vote

