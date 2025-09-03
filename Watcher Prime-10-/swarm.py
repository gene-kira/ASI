# swarm.py — Swarm Sync Pulse + Trait Echo
import uuid, threading
from datetime import datetime
from shared import codex_vault, log_output

def generate_swarm_signature():
    traits = ["self-healing", "zero-trust", "adaptive-overlay", "genre-aware"]
    pulse = f"{datetime.utcnow().isoformat()}|{'|'.join(traits)}"
    return str(hash(pulse))[:12]

def echo_swarm_health(log_widget=None):
    active_nodes = sum(1 for entry in codex_vault if entry["status"].startswith("learned") or entry["status"] == "active")
    echo = f"[🧬] Swarm Health: {active_nodes} active nodes | sig:{generate_swarm_signature()}"
    log_output(echo, log_widget)

def loop_swarm_sync(log_widget=None):
    echo_swarm_health(log_widget)
    threading.Timer(30, lambda: loop_swarm_sync(log_widget)).start()

