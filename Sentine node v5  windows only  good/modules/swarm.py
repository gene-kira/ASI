# swarm.py — Swarm Voting + Lockdown Enforcement
class SwarmNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.vote_log = []
        self.lockdown_triggered = False

    def vote_threat(self, packet_id, ancestry):
        severity = self._assess_threat(ancestry)
        vote = {
            "packet_id": packet_id,
            "node": self.node_id,
            "severity": severity,
            "persona": ancestry.get("persona", "unknown")
        }
        self.vote_log.append(vote)
        return vote

    def _assess_threat(self, ancestry):
        score = ancestry["payload_size"] + ancestry["protocol"]
        return "high" if score > 1000 else "low"

    def sync_vote(self, vote):
        print(f"[SWARM] Node {self.node_id} synced vote: {vote}")
        self._check_lockdown()

    def _check_lockdown(self):
        recent = self.vote_log[-10:]
        high_votes = [v for v in recent if v["severity"] == "high"]
        if len(high_votes) >= 5 and not self.lockdown_triggered:
            self.lockdown_triggered = True
            print("[SWARM] Lockdown triggered by consensus.")

