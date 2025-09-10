# persona_engine.py

import random

class PersonaEngine:
    def __init__(self, gui, event_bus):
        self.gui = gui
        self.event_bus = event_bus
        self.active = False
        self.persona_list = [
            "Decoy: Analyst",
            "Decoy: SysAdmin",
            "Decoy: ThreatHunter",
            "Decoy: Forensic AI",
            "Decoy: Compliance Auditor"
        ]

    def inject(self):
        """
        Randomly selects and activates a decoy persona.
        Updates GUI and logs symbolic feedback.
        """
        if self.active:
            return self.event_bus.log("[PERSONA] Injection skipped — already active.")

        persona = random.choice(self.persona_list)
        self.gui.persona_status.config(text=f"Persona: {persona}", foreground="blue")
        self.active = True
        return self.event_bus.log(f"[PERSONA] Injected {persona}")

    def deactivate(self):
        """
        Deactivates the current persona and resets GUI.
        """
        self.gui.persona_status.config(text="Persona: Dormant", foreground="gray")
        self.active = False
        return self.event_bus.log("[PERSONA] Persona deactivated — mask removed.")

    def is_active(self):
        """
        Returns whether a persona is currently active.
        """
        return self.active

