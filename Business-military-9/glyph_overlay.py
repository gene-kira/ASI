# glyph_overlay.py

class GlyphOverlay:
    def __init__(self):
        self.glyph = "∅"

    def update(self, codex, persona_active, ingest_count):
        if persona_active:
            self.glyph = "🜏"
        elif "phantom node" in codex["threat_signatures"]:
            self.glyph = "⟁"
        elif ingest_count > 100:
            self.glyph = "⚠"
        else:
            self.glyph = "◉"

    def render(self):
        return self.glyph

