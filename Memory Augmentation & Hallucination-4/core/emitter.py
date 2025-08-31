# 📡 core/emitter.py — SwarmSync Emitter
class SwarmSyncEmitter:
    def emit(self, pulse):
        packet = {
            "source": pulse.source,
            "weight": pulse.weight,
            "entropy": pulse.entropy,
            "lineage": pulse.lineage
        }
        print(f"[📡 SwarmSync] {packet}")
        return packet

