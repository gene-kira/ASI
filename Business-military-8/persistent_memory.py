# persistent_memory.py

class PersistentMemory:
    def __init__(self):
        self.memory = {
            "threats": [],
            "personas": [],
            "codex_history": []
        }

    def record_threat(self, threat):
        self.memory["threats"].append(threat)

    def record_persona(self, persona):
        self.memory["personas"].append(persona)

    def record_codex(self, codex):
        self.memory["codex_history"].append(codex)

    def export(self):
        return dict(self.memory)

