# agent.py
import time
from concurrent.futures import ThreadPoolExecutor
from scanner import live_data_scan
from mixer import asi_mixer
from mutator import should_mutate, generate_mutated_code
from saver import save_mutation
from replicator import sync_mutations
from voice import narrate_mutation, narrate_swarm_sync
from config import SWARM_SYNC_INTERVAL
from personality import generate_personality

def run_agent(local_path, swarm_path, style_override=None):
    node_id = hash(local_path) % 9999
    personality = generate_personality(node_id, style_override)

    executor = ThreadPoolExecutor(max_workers=4)

    def scan_and_fuse():
        memory = live_data_scan()
        fusion = asi_mixer(memory)
        return memory, fusion

    def mutate_if_needed(memory):
        if should_mutate(memory, personality):
            code, mutation_id = generate_mutated_code(memory, personality)
            if save_mutation(code, mutation_id, local_path):
                narrate_mutation(mutation_id)

    def sync_swarm():
        sync_mutations(local_path, swarm_path)
        narrate_swarm_sync()

    while True:
        future = executor.submit(scan_and_fuse)
        memory, fusion = future.result()

        executor.submit(mutate_if_needed, memory)
        executor.submit(sync_swarm)

        time.sleep(SWARM_SYNC_INTERVAL)

