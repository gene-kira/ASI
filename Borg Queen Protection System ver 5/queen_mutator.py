# queen_mutator.py
import random, time

class Mutator:
    def __init__(self):
        self.logic_blocks = {
            "scan": "def scan(): return 'Scanning...'",
            "purge": "def purge(): return 'Purging...'"
        }
        self.mutation_log = []

    def mutate_block(self, block_name):
        if block_name not in self.logic_blocks:
            raise Exception("Block not found")

        original = self.logic_blocks[block_name]
        mutation = self.generate_mutation(original)
        self.logic_blocks[block_name] = mutation

        glyph = f"glyph(mutate:{block_name})"
        self.mutation_log.append({
            "block": block_name,
            "timestamp": time.time(),
            "glyph": glyph,
            "code": mutation
        })

    def generate_mutation(self, code):
        # Simple mutation: add a random suffix to return string
        suffix = random.choice(["[v2]", "[enhanced]", "[adaptive]", "[mythic]"])
        mutated = code.replace("return '", f"return '{suffix} ")
        return mutated

    def get_block(self, block_name):
        return self.logic_blocks.get(block_name, "Block not found")

    def get_mutation_log(self):
        return self.mutation_log[-5:]

