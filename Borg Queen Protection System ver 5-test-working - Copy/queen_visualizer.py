# queen_visualizer.py
import random

class Visualizer:
    def __init__(self):
        self.fx_queue = []
        self.glyph_map = {
            "scan": "🔍",
            "purge": "🔥",
            "encrypt": "🔐",
            "anomaly": "⚠️",
            "mutate": "🧬",
            "vault": "🗄️",
            "firewall": "🛡️",
            "telemetry": "📡"
        }

    def render_fx(self, fx):
        aura = f"Aura[{fx['color']}]: {fx['burst']} x{fx['intensity']}"
        self.fx_queue.append(aura)
        return aura

    def render_glyph(self, audit_entry):
        for key in self.glyph_map:
            if key in audit_entry:
                return f"{self.glyph_map[key]} {audit_entry}"
        return f"✨ {audit_entry}"

    def render_overlay(self, audit_log, fx_list):
        visuals = []
        for entry in audit_log:
            visuals.append(self.render_glyph(entry))
        for fx in fx_list:
            visuals.append(self.render_fx(fx))
        return visuals[-10:]

