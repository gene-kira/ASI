# 🧬 modules/replicator.py — Replicator Node Engine
from random import randint, choice

class ReplicatorNode:
    def __init__(self, id, generation=0):
        self.id = id
        self.generation = generation
        self.lineage = [id]

    def replicate(self):
        new_id = f"{self.id}-R{randint(1000,9999)}"
        clone = ReplicatorNode(new_id, self.generation + 1)
        clone.lineage = self.lineage + [new_id]
        return clone

    def mutate_logic(self):
        mutation = ''.join(choice("∆ΩΨΣΞ") for _ in range(3))
        return f"🧬 Mutation[{self.id}]: {mutation}"

