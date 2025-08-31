# 👁️ modules/vision.py — Double Vision Overlay
class DoubleVisionOverlay:
    def render(self, pulse, hallucination):
        return [
            f"👁️ Real: {pulse.source} | Entropy: {pulse.entropy:.2f}",
            f"👁️ Mirror: {hallucination}"
        ]

