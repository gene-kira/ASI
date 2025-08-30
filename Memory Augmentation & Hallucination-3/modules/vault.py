# 📜 modules/vault.py — Game Trigger & Memory Vault
import time

class GameTriggerMemoryVault:
    def __init__(self):
        self.vault = []

    def log_event(self, pulse, event_type, details):
        entry = {
            "timestamp": time.strftime("%H:%M:%S"),
            "source": pulse.source,
            "type": event_type,
            "details": details
        }
        self.vault.append(entry)

    def recall_recent(self, count=5):
        return self.vault[-count:]

    def search_by_type(self, event_type):
        return [e for e in self.vault if e["type"] == event_type]

    def purge(self):
        self.vault = []

