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
            "threat_signatures": ["ASI", "ghost sync", "telemetry spoof"]
        }

    def mutate(self, event_log):
        """
        Scans the event log for threat patterns and rewrites purge logic accordingly.
        """
        for entry in event_log:
            msg = entry.get("message", "").lower()
            if "ghost sync" in msg:
                self.codex["purge_rules"]["telemetry"] = 10
                if "phantom node" not in self.codex["threat_signatures"]:
                    self.codex["threat_signatures"].append("phantom node")

    def get_purge_delay(self, category):
        """
        Returns the purge delay for a given data category.
        """
        return self.codex["purge_rules"].get(category, 60)

    def sync_with(self, other_codex):
        """
        Merges purge rules and threat signatures from another node's codex.
        """
        if not isinstance(other_codex, dict):
            return

        # Merge purge rules
        for key, value in other_codex.get("purge_rules", {}).items():
            self.codex["purge_rules"][key] = value

        # Merge threat signatures
        for sig in other_codex.get("threat_signatures", []):
            if sig not in self.codex["threat_signatures"]:
                self.codex["threat_signatures"].append(sig)

    def export_codex(self):
        """
        Returns a copy of the current codex for sync or audit.
        """
        return {
            "purge_rules": dict(self.codex["purge_rules"]),
            "threat_signatures": list(self.codex["threat_signatures"])
        }

    def debug_print(self):
        """
        Prints the current codex state for debugging.
        """
        print("=== CODEX STATE ===")
        print("Purge Rules:")
        for k, v in self.codex["purge_rules"].items():
            print(f"  {k}: {v}s")
        print("Threat Signatures:")
        for sig in self.codex["threat_signatures"]:
            print(f"  - {sig}")
        print("===================")

