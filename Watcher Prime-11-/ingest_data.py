# ingest_data.py — Drag-and-Drop Ingest + Genre-Aware Sync + File Type Detection
import uuid, os
from datetime import datetime
from shared import codex_vault, log_output, update_codex_display
from codex import log_event

# 🧠 Genre detection based on symbolic content
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

# 📁 File type detection based on extension
def detect_file_type(path):
    ext = os.path.splitext(path)[1].lower()
    if ext == ".txt":
        return "Text"
    elif ext == ".json":
        return "JSON"
    elif ext == ".log":
        return "Log"
    elif ext == ".py":
        return "Python Script"
    elif ext in [".cfg", ".ini"]:
        return "Config"
    else:
        return "Unknown"

# 🔁 Swarm sync pulse
def broadcast_swarm_sync(source, genre, file_type, log_widget=None):
    pulse = f"{source}|{genre}|{file_type}|{datetime.utcnow().isoformat()}"
    hash_sig = str(hash(pulse))
    log_output(f"[🔁] Swarm sync: {source} → {genre} ({file_type}) | sig: {hash_sig[:10]}", log_widget)

# 📂 Main ingest function
def ingest_file(path, codex_widget=None, log_widget=None):
    try:
        # Clean drag-and-drop path
        clean_path = path.strip().strip("{").strip("}")
        if not os.path.isfile(clean_path):
            log_output(f"[⚠️] Invalid file path: {clean_path}", log_widget)
            return

        with open(clean_path, "r", encoding="utf-8") as f:
            content = f.read()

        genre = detect_genre_from_content(content)
        file_type = detect_file_type(clean_path)
        hash_value = str(hash(content))

        entry_id = log_event(
            source=f"Ingest:{os.path.basename(clean_path)}",
            event_type="learn",
            hash_value=hash_value,
            status=f"learned:{genre}:{file_type}",
            codex_widget=codex_widget,
            log_widget=log_widget
        )

        broadcast_swarm_sync(f"Ingest:{os.path.basename(clean_path)}", genre, file_type, log_widget)

    except Exception as e:
        log_output(f"[⚠️] Ingest failed: {e}", log_widget)

