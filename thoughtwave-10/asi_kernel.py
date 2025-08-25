class ASIKernel:
    def __init__(self):
        self.symbolic_memory = {}  # {signature: {"weight": int, "tags": [str]}}
        self.mutation_history = []
        self.adaptive_mode = False

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
        top_signature = max(self.symbolic_memory.items(), key=lambda x: x[1]["weight"])
        return {
            "fusion_signature": top_signature[0],
            "weight": top_signature[1]["weight"],
            "tags": top_signature[1]["tags"],
            "adaptive_overlay": "🧠 Evolved" if self.adaptive_mode else "🔄 Learning..."
        }

