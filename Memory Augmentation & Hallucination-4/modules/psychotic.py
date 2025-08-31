# 🧨 modules/psychotic.py — Psychotic Drift Engine
from random import choice, randint

class PsychoticDriftEngine:
    def __init__(self):
        self.distortions = []

    def distort_memory(self, pulse):
        scrambled = ''.join(choice('!?@#%&*') for _ in range(3))
        distorted = f"{pulse.source}:{scrambled}:{randint(1000,9999)}"
        self.distortions.append(distorted)
        return distorted

    def loop_logic(self, pulse):
        return f"{pulse.source}↻{pulse.source}↻{pulse.source}"

    def paranoia_trigger(self, pulse):
        if pulse.entropy > 8.0:
            return f"⚠️ Paranoia: Memory tampering suspected from {pulse.source}"
        return None

