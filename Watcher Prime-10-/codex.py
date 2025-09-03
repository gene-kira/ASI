# codex.py — Symbolic Memory + Self-Destruct Logic
import uuid, json, os, threading
from datetime import datetime
from shared import codex_vault, log_output, update_codex_display

CODEX_FILE = "fusion_codex.json"

def log_event(source, event_type, hash_value, status="active", codex_widget=None, log_widget=None):
    entry = {
        "id": str(uuid.uuid4()),
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
        "hash": hash_value,
        "status": status
    }
    codex_vault.append(entry)
    if codex_widget:
        update_codex_display(codex_widget)
    log_output(f"[📜] {event_type} from {source} | {hash_value[:12]}", log_widget)
    return entry["id"]

def store_rewrite(entry, log_widget=None):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)
    log_output(f"[🔐] Rewrite stored in fusion_codex.json", log_widget)

def trigger_self_destruct(data_id, delay_sec, codex_widget=None, log_widget=None):
    def destroy():
        for entry in codex_vault:
            if entry["id"] == data_id:
                entry["status"] = "destroyed"
        if codex_widget:
            update_codex_display(codex_widget)
        log_output(f"[💥] Data {data_id[:6]} self-destructed after {delay_sec}s", log_widget)
    threading.Timer(delay_sec, destroy).start()

