import json
import os

CODEX_FILE = "fusion_codex.json"

def visualize_codex(path=CODEX_FILE, limit=5):
    if not os.path.exists(path):
        print("⚠️ Fusion codex not found.")
        return

    try:
        with open(path, "r") as f:
            codex = json.load(f)
    except json.JSONDecodeError:
        print("⚠️ Codex file is corrupted or unreadable.")
        return

    print("\n🌌 Fusion Codex Snapshot:")
    for entry in codex[-limit:]:
        print(f"🔁 Logic: {entry.get('logic', '—')}")
        print(f"🕒 Timestamp: {entry.get('timestamp', '—')}")
        print(f"🧠 Trigger: {entry.get('trigger', '—')}")
        print(f"🐝 Consensus: {entry.get('consensus', '—')}\n")

