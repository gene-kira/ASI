# fusion.py

class FusionSignature:
    def __init__(self, node_id, lineage, entropy_trend):
        self.node_id = node_id
        self.lineage = lineage
        self.signature = self.generate_signature(entropy_trend)

    def generate_signature(self, entropy_trend):
        # Create a symbolic glyph based on entropy average and lineage depth
        base_entropy = sum(entropy_trend) / len(entropy_trend)
        lineage_depth = len(set(self.lineage))
        glyph = f"{self.node_id[:2]}-{int(base_entropy * 10)}:{lineage_depth}"
        return glyph

