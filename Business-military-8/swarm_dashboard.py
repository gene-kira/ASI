# swarm_dashboard.py

class SwarmDashboard:
    def __init__(self, registry):
        self.registry = registry

    def render_summary(self):
        summary = []
        for node_id, data in self.registry.nodes.items():
            codex = data["codex"]
            glyph = data.get("glyph", "∅")
            threats = len(codex.get("threat_signatures", []))
            summary.append(f"{node_id}: Glyph {glyph}, Threats {threats}")
        return "\n".join(summary)

