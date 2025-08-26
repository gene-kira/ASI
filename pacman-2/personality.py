# personality.py

import random

def generate_personality(node_id):
    styles = ["aggressive", "curious", "minimalist", "chaotic", "symbiotic"]
    tone = random.choice(styles)
    return {
        "node_id": node_id,
        "mutation_style": tone,
        "curiosity_bias": random.randint(50, 100),
        "density_threshold": random.randint(40, 80),
        "novelty_threshold": random.randint(70, 95)
    }

