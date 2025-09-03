# ingest_data.py — Drag-and-Drop Ingest + Genre-Aware Sync
import uuid, os
from datetime import datetime
from shared import codex_vault, log_output, update_codex_display
from codex import log_event

def detect_genre_from_content(content):
    content = content.lower()
    if any(term in content for term in ["frame", "enemy", "hitbox", "reload"]):
        return "Shooter"
    elif any(term in content for term in ["quest", "dialogue", "npc", "inventory"]):
        return "RPG"
    elif any(term in content for term in ["build", "resource", "harvest", "unit"]):
        return "RTS"
    elif any(term in content for term in ["battle royale", "drop zone", "circle"]):
        return "Battle Royale"
    return "Unknown"

def broadcast_swarm_sync(source, genre, log_widget=None):
    pulse = f"{source}|{genre}|{datetime.utcnow().isoformat()}"
    hash_sig = str(hash(pulse))
    log_output(f"[🔁] Swarm sync pulse: {source} → {genre} | sig: {hash_sig[:10]}", log_widget)

def ingest_file(path, codex_widget=None, log_widget=None):
    try:
        if not os.path.isfile(path):
            log_output(f"[⚠️] Invalid file path: {path}", log_widget)
            return

        with open(path, "r", encoding="utf-8") as f:
            content = f.read()

        genre = detect_genre_from_content(content)
        hash_value = str(hash(content))
        log_event(
            source=f"Ingest:{os.path.basename(path)}",
            event_type="learn",
            hash_value=hash_value,
            status=f"learned:{genre}",
            codex_widget=codex_widget,
            log_widget=log_widget
        )

        broadcast_swarm_sync(f"Ingest:{os.path.basename(path)}", genre, log_widget)

    except Exception as e:
        log_output(f"[⚠️] Ingest failed: {e}", log_widget)

