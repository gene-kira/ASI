# persona_engine.py

from datetime import datetime
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
        self.history = []

    def inject(self):
        if self.active:
            return self.event_bus.log("[PERSONA] Injection skipped — already active.")
        persona = self.persona_list.pop(0)
        self.persona_list.append(persona)
        self.gui.persona_status.config(text=f"Persona: {persona}", foreground="blue")
        self.active = True
        self.history.append((datetime.now().isoformat(), persona))
        return self.event_bus.log(f"[PERSONA] Injected {persona}")

    def deactivate(self):
        self.gui.persona_status.config(text="Persona: Dormant", foreground="gray")
        self.active = False
        return self.event_bus.log("[PERSONA] Persona deactivated — mask removed.")

    def is_active(self):
        return self.active

    def export_history(self):
        return list(self.history)

