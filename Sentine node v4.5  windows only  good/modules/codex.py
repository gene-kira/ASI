# codex.py — Symbolic Mutation Engine
import time

class SymbolicCodex:
    def __init__(self):
        self.entries = []

    def mutate(self, event_type, source, detail):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        symbol = {
            "threat": "⚔️",
            "persona": "🎭",
            "swarm": "🧠",
            "telemetry": "🛰️"
        }.get(event_type, "❓")
        entry = f"{symbol} [{timestamp}] {source}: {detail}"
        self.entries.append(entry)
        return entry

    def get_recent(self, count=10):
        return self.entries[-count:]

