# zero_trust_core.py
import hashlib
import time
import random

class ZeroTrustCore:
    def __init__(self):
        self.trust_scores = {}
        self.ephemeral_logs = []

    def generate_glyph_key(self, agent_id):
        seed = f"{agent_id}-{time.time()}"
        glyph = hashlib.sha256(seed.encode()).hexdigest()[:16]
        return glyph

    def score_access(self, agent_id, behavior):
        score = random.uniform(0, 1)
        self.trust_scores[agent_id] = score
        self.ephemeral_logs.append((agent_id, behavior, score))
        if len(self.ephemeral_logs) > 50:
            self.ephemeral_logs.pop(0)
        return score

    def is_access_allowed(self, agent_id):
        score = self.trust_scores.get(agent_id, 0)
        return score > 0.6

    def rewrite_rules(self, threat_level):
        if threat_level > 0.8:
            print("🔁 Rewriting access logic: tightening rules")
            for agent in self.trust_scores:
                self.trust_scores[agent] *= 0.5

    def purge_logs(self):
        self.ephemeral_logs = []

    def get_recent_activity(self):
        return self.ephemeral_logs[-10:]

