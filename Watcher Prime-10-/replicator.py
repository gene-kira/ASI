# replicator.py — Mutation-Aware Clone Engine
import uuid, random, hashlib, threading
from datetime import datetime
from codex import log_event
from gui import codex_vault, update_codex_display, log_output

def spawn_clone():
    traits = random.sample(["stealth", "fallback", "anomaly_hunter"], k=2)
    clone_id = f"Clone_{uuid.uuid4().hex[:6]}"
    trait_hash = "|".join(traits)

    codex_vault.append({
        "id": clone_id,
        "source": "Replicator",
        "timestamp": datetime.utcnow().isoformat(),
        "hash": trait_hash,
        "status": "active"
    })
    update_codex_display()
    sync_pulse(clone_id, trait_hash)
    log_output(f"[🧬] Spawned {clone_id} with traits: {', '.join(traits)}")
    log_event("Replicator", "clone", trait_hash)

def sync_pulse(source, trait_hash):
    pulse = hashlib.sha256((source + trait_hash).encode()).hexdigest()
    log_output(f"[🔁] Swarm sync from {source} | hash: {pulse[:10]}")

def loop_replicate():
    spawn_clone()
    threading.Timer(30, loop_replicate).start()

