# 🔁 core/fusion.py — Fusion Feedback Loop
class FusionFeedbackLoop:
    def update(self, pulse):
        signature = self.generate_signature(pulse)
        print(f"[🔁 Fusion] Signature stored: {signature}")
        return signature

    def generate_signature(self, pulse):
        return f"{pulse.source}:{pulse.entropy:.2f}:{pulse.weight:.2f}"

