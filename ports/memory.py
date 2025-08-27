# memory.py

class NodeMemory:
    def __init__(self):
        self.pulse_history = []     # Stores entropy, weight, timestamp of pulses
        self.mutation_log = []      # Stores MutationEvent objects

    def record_pulse(self, pulse):
        self.pulse_history.append({
            "entropy": pulse.entropy,
            "weight": pulse.weight,
            "timestamp": pulse.timestamp if hasattr(pulse, "timestamp") else "unknown"
        })

    def record_mutation(self, mutation):
        self.mutation_log.append(mutation)

    def replay(self):
        # Return last 10 symbolic events for dashboard playback
        return self.pulse_history[-10:]

