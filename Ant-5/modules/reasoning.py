import os
from core.mutation import MutationHooks

class ReasoningEngine:
    def __init__(self, target_file="main.py", mutation_hook=None):
        self.target = target_file
        self.mutator = mutation_hook or MutationHooks()

    def scan_and_repair(self):
        try:
            with open(self.target, "r") as f:
                code = f.read()
            if "time.sleep(10)" in code:
                mutated = code.replace("time.sleep(10)", "time.sleep(5)")
                with open(self.target, "w") as f:
                    f.write(mutated)
                self.mutator.log_mutation("Self-healing: sleep(10) → sleep(5)")
        except Exception as e:
            self.mutator.log_mutation(f"Repair failed: {e}")

