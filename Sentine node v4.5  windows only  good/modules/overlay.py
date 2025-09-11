# overlay.py
class PersonaManager:
    def __init__(self):
        self.active_personas = []

    def deploy_personas(self):
        self.active_personas = ["decoy_alpha", "observer_beta"]
        print("[OVERLAY] Personas deployed:", self.active_personas)

    def adapt_roles(self, state):
        # Rotate or mutate personas based on state
        pass

