# persona.py

# 🧠 Persona Memory Engine
class PersonaMemory:
    def __init__(self):
        self.encounters = {}
        self.thresholds = {}

    def record(self, threat_type):
        self.encounters[threat_type] = self.encounters.get(threat_type, 0) + 1
        self.adjust_threshold(threat_type)

    def adjust_threshold(self, threat_type):
        count = self.encounters[threat_type]
        self.thresholds[threat_type] = max(1, 5 - count // 3)

# 🎭 Persona Status Tracker
persona_status = {}

# 🎭 Adaptive Persona Class
class AdaptivePersona:
    def __init__(self, name, traits):
        self.name = name
        self.traits = traits
        self.memory = PersonaMemory()
        self.active = False
        persona_status[self.name] = False

    def evaluate_trigger(self, threat_type, origin):
        self.memory.record(threat_type)
        threshold = self.memory.thresholds.get(threat_type, 5)
        if self.memory.encounters[threat_type] >= threshold:
            self.activate(threat_type, origin)

    def activate(self, threat_type, origin):
        self.active = True
        persona_status[self.name] = True
        print(f"[Persona Activated] {self.name} evolved trigger → {threat_type} from {origin}")
        self.perform_action(threat_type)

    def perform_action(self, threat_type):
        action = self.traits["actions"].get(threat_type, "Observe")
        print(f"[{self.name}] Action: {action}")

# 🎭 Persona Definitions
personas = [
    AdaptivePersona("ThreatHunter", {
        "triggers": ["backdoor_leak", "ghost_sync"],
        "actions": {
            "backdoor_leak": "Trace Source",
            "ghost_sync": "Deploy PhantomNode"
        }
    }),
    AdaptivePersona("ComplianceAuditor", {
        "triggers": ["personal_data", "country_violation"],
        "actions": {
            "personal_data": "Flag for Audit",
            "country_violation": "Block Transmission"
        }
    }),
    AdaptivePersona("GhostSync", {
        "triggers": ["telemetry_anomaly"],
        "actions": {
            "telemetry_anomaly": "Inject Decoy Glyph"
        }
    })
]

# 🔄 Trigger Evaluation Router
def evaluate_personas(threat_type, origin):
    for persona in personas:
        persona.evaluate_trigger(threat_type, origin)

