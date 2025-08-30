# 🧬 core/pulse.py — DataPulse Engine
import math
from collections import Counter

class DataPulse:
    def __init__(self, source, payload):
        self.source = source
        self.payload = payload
        self.weight = self.calculate_weight()
        self.entropy = self.calculate_entropy()
        self.lineage = [source]

    def calculate_weight(self):
        return len(self.payload) / 1024  # Normalize to kilobytes

    def calculate_entropy(self):
        freq = Counter(self.payload)
        total = sum(freq.values())
        return -sum((count / total) * math.log2(count / total) for count in freq.values())

