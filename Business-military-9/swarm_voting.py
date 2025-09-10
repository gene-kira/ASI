# swarm_voting.py

from collections import Counter

class SwarmVoting:
    def __init__(self, registry):
        self.registry = registry

    def tally_votes(self):
        all_signatures = []
        for node in self.registry.nodes.values():
            codex = node.get("codex", {})
            all_signatures.extend(codex.get("threat_signatures", []))
        return Counter(all_signatures)

    def get_top_threats(self, count=3):
        votes = self.tally_votes()
        return votes.most_common(count)

