# codex.py — Symbolic Memory + Self-Destruct Logic
import uuid, json, os, threading
from datetime import datetime
from gui import codex_vault, update_codex_display, log_output

CODEX_FILE = "fusion_codex.json"

# 📥 Log symbolic event to Codex Vault
def log_event(source, event_type, hash_value, status="active"):
    entry = {
        "id": str(uuid.uuid4()),
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
        "hash": hash_value,
        "status": status
    }
    codex_vault.append(entry)
    update_codex_display()
    log_output(f"[📜] {event_type} from {source} | {hash_value[:12]}")
    return entry["id"]

# 🔐 Store rewrite logic persistently
def store_rewrite(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)
    log_output(f"[🔐] Rewrite stored in fusion_codex.json")

# 💥 Trigger timed self-destruct
def trigger_self_destruct(data_id, delay_sec):
    def destroy():
        for entry in codex_vault:
            if entry["id"] == data_id:
                entry["status"] = "destroyed"
        update_codex_display()
        log_output(f"[💥] Data {data_id[:6]} self-destructed after {delay_sec}s")
    threading.Timer(delay_sec, destroy).start()

