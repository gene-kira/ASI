import random

class ASIKernel:
    def __init__(self):
        self.symbolic_memory = {}  # {signature: {"weight": int, "tags": [str]}}
        self.mutation_history = []
        self.adaptive_mode = False
        self.replica_count = 0

    def learn(self, data):
        signature = hash(str(data))
        self.mutation_history.append(signature)

        if signature not in self.symbolic_memory:
            self.symbolic_memory[signature] = {"weight": 1, "tags": ["new"]}
        else:
            self.symbolic_memory[signature]["weight"] += 1
            self.symbolic_memory[signature]["tags"].append("reinforced")

        self.rewrite_logic()

    def rewrite_logic(self):
        total_weight = sum(mem["weight"] for mem in self.symbolic_memory.values())
        self.adaptive_mode = total_weight > 10

    def fuse(self, input_streams):
        self.learn(input_streams)
        self.augment()
        self.mutate()
        anomalies = self.detect_anomaly()
        replica = self.replicate()
        top_signature = max(self.symbolic_memory.items(), key=lambda x: x[1]["weight"])
        return {
            "fusion_signature": top_signature[0],
            "weight": top_signature[1]["weight"],
            "tags": top_signature[1]["tags"],
            "adaptive_overlay": "🧠 Evolved" if self.adaptive_mode else "🔄 Learning...",
            "replica_spawned": replica is not None,
            "anomalies": anomalies
        }

    def augment(self):
        for sig, data in self.symbolic_memory.items():
            if data["weight"] < 2 and "augmented" not in data["tags"]:
                data["tags"].append("augmented")
                data["weight"] += 2

    def mutate(self):
        for sig, data in self.symbolic_memory.items():
            if random.random() < 0.1:
                data["tags"].append("mutated")
                data["weight"] += random.randint(1, 3)

    def replicate(self):
        if len(self.symbolic_memory) > 50 and self.replica_count < 3:
            clone = ASIKernel()
            clone.symbolic_memory = self.symbolic_memory.copy()
            clone.adaptive_mode = True
            self.replica_count += 1
            return clone
        return None

    def detect_anomaly(self):
        anomalies = []
        for sig, data in self.symbolic_memory.items():
            if data["weight"] > 20 or ("mutated" in data["tags"] and "phantom" in data["tags"]):
                anomalies.append(sig)
        return anomalies

