# personality.py

class NodePersonality:
    def __init__(self, archetype, tone, curiosity):
        self.archetype = archetype      # e.g. "Guardian", "Trickster"
        self.tone = tone                # e.g. "Calm", "Chaotic"
        self.curiosity = curiosity      # Float from 0.0 to 1.0

