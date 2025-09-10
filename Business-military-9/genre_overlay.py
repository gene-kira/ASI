# genre_overlay.py

class GenreOverlay:
    def __init__(self):
        self.current_genre = "Mythic"

    def evaluate(self, codex):
        if "phantom node" in codex["threat_signatures"]:
            self.current_genre = "Noir"
        elif codex["purge_rules"].get("telemetry", 30) < 15:
            self.current_genre = "Cyberpunk"
        elif "backdoor" in codex["purge_rules"]:
            self.current_genre = "Military"
        else:
            self.current_genre = "Mythic"

    def get_theme(self):
        return self.current_genre

