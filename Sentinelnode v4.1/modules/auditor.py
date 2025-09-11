class ComplianceAuditor:
    def __init__(self, narrator):
        self.narrator = narrator
        self.policies = {"no_root_access": True, "encrypted_only": True}
    def audit(self, packet):
        violations = []
        if packet.user == "root" and self.policies["no_root_access"]:
            violations.append("Root access violation")
        if "unencrypted" in packet.features and self.policies["encrypted_only"]:
            violations.append("Unencrypted traffic")
        for v in violations:
            self.narrator.warn(v)
        return violations

