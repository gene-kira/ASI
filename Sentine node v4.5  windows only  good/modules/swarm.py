# swarm.py — Swarm-Wide Threat Voting
import random

class SwarmNode:
    def __init__(self, node_id):
        self.node_id = node_id
        self.vote_log = []

    def vote_threat(self, packet_id, ancestry):
        severity = self._assess_threat(ancestry)
        vote = {
            "packet_id": packet_id,
            "node": self.node_id,
            "severity": severity
        }
        self.vote_log.append(vote)
        return vote

    def _assess_threat(self, ancestry):
        score = ancestry["payload_size"] + ancestry["protocol"]
        return "high" if score > 1000 else "low"

    def sync_vote(self, vote):
        # Placeholder for encrypted sync
        print(f"[SWARM] Node {self.node_id} synced vote: {vote}")

