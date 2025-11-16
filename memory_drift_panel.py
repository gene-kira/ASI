# memory_drift_panel.py

import time
import random

class MemoryDriftPanel:
    def __init__(self):
        self.sync_drift = 0.0
        self.glyph_echoes = 0
        self.paradox_residue = 0
        self.drift_index = 0.0
        self.alpha = 1.0
        self.beta = 0.01
        self.gamma = 0.05

    def update_metrics(self):
        # Simulate drift evolution
        self.sync_drift = round(random.uniform(10.0, 15.0), 2)
        self.glyph_echoes += random.randint(50, 150)
        self.paradox_residue += random.randint(1, 10)

    def calculate_drift_index(self):
        self.drift_index = (
            self.alpha * self.sync_drift +
            self.beta * self.glyph_echoes +
            self.gamma * self.paradox_residue
        )
        return round(self.drift_index, 3)

    def display_panel(self):
        print("\n=== MEMORY DRIFT PANEL ===")
        print(f"Sync Drift %     : {self.sync_drift}%")
        print(f"Glyph Echoes     : {self.glyph_echoes}")
        print(f"Paradox Residue  : {self.paradox_residue}")
        print(f"Drift Index      : {self.calculate_drift_index()}")
        print("==========================")

    def run(self, cycles=5, delay=2):
        for _ in range(cycles):
            self.update_metrics()
            self.display_panel()
            time.sleep(delay)

if __name__ == "__main__":
    panel = MemoryDriftPanel()
    panel.run()

