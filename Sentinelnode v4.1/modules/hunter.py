class ThreatHunter:
    def scan(self, packet):
        if "live" not in packet.features:
            raise ValueError("Non-live packet rejected")
        if "anomaly" in packet.features or "ASI" in packet.features:
            return "threat"
        return "clean"

