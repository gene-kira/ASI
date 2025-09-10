# daemon.py

import uuid, time, threading
from datetime import datetime, timedelta
import hashlib
from queue import Queue

from codex import classify, PURGE_RULES
from sync import encrypt_payload
from persona import evaluate_personas
from gui import launch_gui

# 🧠 Local Memory Store
memory_store = {}
event_queue = Queue()

# 📜 Symbolic Feedback
def narrate(event, data_id):
    log = f"[MythicLog] {event} → {data_id}"
    print(log)
    event_queue.put(log)

# 🧿 Glyph Generator
def generate_glyph(data):
    return f"GLYPH-{hashlib.sha256(data.encode()).hexdigest()[:8]}"

# 🧠 Ingest Logic
def ingest(data, origin="unknown"):
    data_id = str(uuid.uuid4())
    tags = classify(data)
    glyph = generate_glyph(data)
    memory_store[data_id] = {
        "data": data,
        "tags": tags,
        "glyph": glyph,
        "timestamp": datetime.utcnow()
    }
    narrate("Ingested", data_id)
    for tag in tags:
        evaluate_personas(tag, origin)

# 🧼 Purge Logic
def purge_check():
    now = datetime.utcnow()
    for data_id, entry in list(memory_store.items()):
        for tag in entry["tags"]:
            expire_time = entry["timestamp"] + PURGE_RULES.get(tag, timedelta(seconds=10))
            if now >= expire_time:
                narrate("Purged", data_id)
                del memory_store[data_id]
                break

# 🔁 Background Purge Loop
def purge_loop():
    while True:
        purge_check()
        time.sleep(1)

# 🚀 Daemon Boot Sequence
def daemon_loop():
    print("\n🧠 MythicNode Booting...")
    print("🔐 Sync overlay initialized")
    print("🧿 Glyph engine online")
    print("🎭 Persona memory loaded")
    print("🛡️ Defense node active\n")

    # Start purge loop in background thread
    threading.Thread(target=purge_loop, daemon=True).start()

    # Launch GUI in main thread (Windows-safe)
    launch_gui(memory_store, event_queue)

