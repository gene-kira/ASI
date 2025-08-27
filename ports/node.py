# node.py

from random import choice
from personality import NodePersonality
from memory import NodeMemory
from fusion import FusionSignature

class Node:
    def __init__(self, id):
        self.id = id
        self.pulses = []             # List of DataPulse objects
        self.lineage = []            # Ancestor node IDs
        self.mutations = []          # List of MutationEvent objects
        self.last_entropy = 0        # Latest entropy value

        # 🧬 Assign a mythic personality
        self.personality = self.assign_personality()

        # 🧠 Memory replay engine
        self.memory = NodeMemory()

        # 🔗 Fusion signature (generated after mutation)
        self.fusion = None

    def assign_personality(self):
        return choice([
            NodePersonality("Guardian", "Calm", 0.3),
            NodePersonality("Trickster", "Chaotic", 0.7),
            NodePersonality("Strategist", "Focused", 0.5),
            NodePersonality("Dreamer", "Curious", 0.9)
        ])

