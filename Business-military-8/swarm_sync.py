# swarm_sync.py

from datetime import datetime

class SwarmSync:
    def __init__(self, codex_mutator):
        self.codex = codex_mutator
        self.last_sync_time = None
        self.sync_log = []

    def simulate_sync(self):
        """
        Simulates a sync event with another node's codex.
        This would be replaced with real network sync logic in production.
        """
        other_codex = {
            "purge_rules": {
                "telemetry": 15,
                "mac_ip": 20
            },
            "threat_signatures": [
                "ghost sync",
                "phantom node"
            ]
        }

        self.codex.sync_with(other_codex)
        self.last_sync_time = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[SYNC] Swarm sync complete @ {self.last_sync_time}"
        self.sync_log.append(log_entry)
        return log_entry

    def get_sync_status(self):
        """
        Returns the latest sync status.
        """
        if self.last_sync_time:
            return f"Last sync: {self.last_sync_time}"
        return "No sync performed yet."

    def export_sync_log(self):
        """
        Returns the full sync history.
        """
        return list(self.sync_log)

