# codex_mutator.py

from datetime import datetime

class CodexMutator:
    def __init__(self):
        self.codex = {
            "purge_rules": {
                "backdoor": 3,
                "mac_ip": 30,
                "personal": 86400,
                "telemetry": 30
            },
            "threat_signatures": ["ASI", "ghost sync"]
        }
        self.ancestry = []

    def mutate(self, event_log):
        for entry in event_log:
            msg = entry.get("message", "").lower()
            if "ghost sync" in msg:
                self.codex["purge_rules"]["telemetry"] = 10
                if "phantom node" not in self.codex["threat_signatures"]:
                    self.codex["threat_signatures"].append("phantom node")
                self.record_mutation("ghost sync → phantom node")

    def record_mutation(self, reason):
        snapshot = {
            "timestamp": datetime.now().isoformat(),
            "reason": reason,
            "codex": self.export_codex()
        }
        self.ancestry.append(snapshot)

    def export_codex(self):
        return {
            "purge_rules": dict(self.codex["purge_rules"]),
            "threat_signatures": list(self.codex["threat_signatures"])
        }

    def export_ancestry(self):
        return list(self.ancestry)

    def sync_with(self, other_codex):
        self.codex["purge_rules"].update(other_codex.get("purge_rules", {}))
        for sig in other_codex.get("threat_signatures", []):
            if sig not in self.codex["threat_signatures"]:
                self.codex["threat_signatures"].append(sig)

