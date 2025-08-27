# pulse.py

from collections import Counter
import math

class DataPulse:
    def __init__(self, source, payload):
        self.source = source
        self.payload = payload
        self.weight = self.calculate_weight()
        self.entropy = self.calculate_entropy()
        self.lineage = [source]

    def calculate_weight(self):
        # Symbolic weight based on payload size
        return len(self.payload) / 1024

    def calculate_entropy(self):
        # Shannon entropy calculation
        freq = Counter(self.payload)
        total = sum(freq.values())
        return -sum((count / total) * math.log2(count / total) for count in freq.values())

