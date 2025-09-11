import time
class SymbolicMemory:
    def tag(self, packet, threat_score):
        return {
            "origin": packet.origin,
            "pid": packet.pid,
            "user": packet.user,
            "trust_level": threat_score,
            "timestamp": time.time()
        }

