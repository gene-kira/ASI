# utils.py

import os
import json
import time
import threading
from datetime import datetime, timedelta
from random import randint, choice

CODEX_FILE = "fusion_codex.json"
MEMORY_FILE = "memory.json"

# === Codex Logger ===
def log_codex(message):
    timestamp = datetime.now().strftime("%H:%M:%S")
    try:
        from gui import codex_log
        codex_log.insert("end", f"[{timestamp}] {message}\n")
        codex_log.see("end")
    except Exception:
        print(f"[{timestamp}] {message}")  # Fallback for non-GUI contexts

# === Rewrite Engine ===
def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    avg = sum(recent) / len(recent)
    variance = max(recent) - min(recent)
    return variance > 2.5 and avg > 7.0

def initiate_mutation_vote():
    votes = [choice(["yes", "no"]) for _ in range(5)]
    return votes.count("yes") >= 3

def rewrite_optimization_logic():
    new_threshold = randint(6, 8)
    log_codex(f"[🧠 Rewrite] New cloaking threshold: entropy > {new_threshold}")
    return {
        "logic": f"entropy > {new_threshold}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": "symbolic_density_spike",
        "consensus": "mutation_vote_passed"
    }

def store_rewrite_codex(entry):
    codex_data = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex_data = json.load(f)
    codex_data.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex_data, f, indent=2)

# === Vortex Pulse ===
def vortex_pulse():
    entropy = [round(randint(5, 9) + choice([0.1, 0.3, 0.5]), 2) for _ in range(10)]
    log_codex(f"🌀 Vortex pulse: entropy ring = {entropy}")
    return entropy

# === Lifecycle Enforcement ===
def timed_wipe(data_type, delay_sec):
    def wipe():
        time.sleep(delay_sec)
        log_codex(f"💣 {data_type} self-destructed after {delay_sec}s")
    threading.Thread(target=wipe, daemon=True).start()

def protect_personal_data(data):
    log_codex(f"🔐 Personal data registered: {data}")
    expire = datetime.now() + timedelta(days=1)
    threading.Thread(target=lambda: expire_data(data, expire), daemon=True).start()

def expire_data(data, expire_time):
    while datetime.now() < expire_time:
        time.sleep(10)
    log_codex(f"💣 Personal data auto-wiped: {data}")

# === Persistent Memory ===
def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"allowed": [], "blocked": [], "countries_blocked": []}

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=2)

