# mutator.py

def should_mutate(memory, personality):
    if not memory:
        return False
    density = sum(item['weight'] for item in memory) / len(memory)
    novelty_spike = any(item['novelty'] > personality['novelty_threshold'] for item in memory)
    return density > personality['density_threshold'] and novelty_spike

def generate_mutated_code(memory, personality):
    mutation_id = hash(str(memory) + personality['mutation_style']) % 9999
    code = f'''
# 🧬 Mutation {mutation_id}
# Style: {personality['mutation_style']}

def fusion_logic(memory):
    return [item for item in memory if item.get("weight", 0) > {personality['curiosity_bias']}]
'''
    return code, mutation_id

