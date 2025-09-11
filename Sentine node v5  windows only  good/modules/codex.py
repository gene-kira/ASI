# codex.py — Symbolic Codex with Mutation Tree
import time, hashlib

class SymbolicCodex:
    def __init__(self):
        self.entries = []
        self.ancestry_ledger = []

    def mutate(self, event_type, source, detail, ancestry=None, parent_hash=None):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        symbol = {
            "threat": "⚔️",
            "persona": "🎭",
            "swarm": "🧠",
            "lockdown": "🛡️"
        }.get(event_type, "❓")
        entry = f"{symbol} [{timestamp}] {source}: {detail}"
        self.entries.append(entry)

        if ancestry:
            hash_input = f"{source}{detail}{timestamp}{parent_hash}".encode()
            ancestry_hash = hashlib.sha256(hash_input).hexdigest()
            self.ancestry_ledger.append({
                "timestamp": timestamp,
                "source": source,
                "detail": detail,
                "hash": ancestry_hash,
                "parent": parent_hash or "root"
            })

        return entry, ancestry_hash

    def get_recent(self, count=10):
        return self.entries[-count:]

    def get_ancestry(self, count=10):
        return self.ancestry_ledger[-count:]

