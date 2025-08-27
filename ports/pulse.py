# pulse.py

from collections import Counter
import math

class DataPulse:
    def __init__(self, source, payload):
        self.source = source              # Node ID that emitted the pulse
        self.payload = payload            # Symbolic data payload
        self.weight = self.calculate_weight()
        self.entropy = self.calculate_entropy()
        self.lineage = [source]           # Initial lineage

    def calculate_weight(self):
        # Symbolic weight based on payload size (in KB)
        return len(self.payload) / 1024

    def calculate_entropy(self):
        # Shannon entropy: measures unpredictability of the payload
        freq = Counter(self.payload)
        total = sum(freq.values())
        return -sum((count / total) * math.log2(count / total) for count in freq.values())

