from modules.codex import SymbolicMemory
from modules.trust import ZeroTrustEngine
from modules.overlay import PersonaOverlay
from modules.hunter import ThreatHunter
from modules.auditor import ComplianceAuditor
from modules.sync import GhostSync
from modules.biodata import BioDataSentinel
from modules.telemetry import FakeTelemetryShield
from modules.aiwall import ZeroTrustAIWall
from modules.destructor import DataDestructionEngine
from modules.ipcontrol import IPAccessControl
from modules.model import AIThreatModel

class SentinelNode:
    def __init__(self, narrator):
        self.codex = SymbolicMemory()
        self.overlay = PersonaOverlay()
        self.trust_engine = ZeroTrustEngine()
        self.narrator = narrator
        self.hunter = ThreatHunter()
        self.auditor = ComplianceAuditor(narrator)
        self.sync = GhostSync()
        self.bio_sentinel = BioDataSentinel()
        self.telemetry = FakeTelemetryShield()
        self.ai_wall = ZeroTrustAIWall()
        self.destructor = DataDestructionEngine(narrator)
        self.ip_control = IPAccessControl(narrator)

    def ingest(self, packet):
        if self.ip_control.evaluate(packet.origin) != "allow":
            return
        if not packet.is_live():
            self.narrator.warn("Rejected: Non-live or simulated packet")
            return
        if not self.ai_wall.verify("AI"):
            self.narrator.warn("AI actor blocked")
            return
        if self.hunter.scan(packet) == "threat":
            self.narrator.log("ThreatHunter flagged anomaly")
        violations = self.auditor.audit(packet)
        if violations:
            self.trust_engine.purge({"pid": packet.pid, "user": packet.user})
            self.overlay.deploy_decoy({"origin": packet.origin})
            self.narrator.log("Compliance violation handled")
            return
        if self.bio_sentinel.scan(packet.user):
            self.destructor.track(packet.pid, "bio")
        threat_score = AIThreatModel.evaluate(packet.features)
        symbol = self.codex.tag(packet, threat_score)
        self.sync.sync(symbol)
        self.destructor.track(symbol["origin"], "mac_ip")
        self.destructor.track(symbol["origin"] + "_telemetry", "telemetry")
        self.telemetry.inject()
        if self.trust_engine.verify(symbol):
            self.narrator.log("Access granted")
        else:
            self.trust_engine.purge(symbol)
            self.overlay.deploy_decoy(symbol)
            self.narrator.log("Threat neutralized")

