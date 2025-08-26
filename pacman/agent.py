# agent.py
import time
from scanner import live_data_scan
from mixer import asi_mixer
from mutator import should_mutate, generate_mutated_code
from saver import save_mutation
from replicator import sync_mutations
from config import SWARM_SYNC_INTERVAL
from voice import narrate_mutation, narrate_swarm_sync

def run_agent(local_path, swarm_path):
    while True:
        memory = live_data_scan()
        fusion = asi_mixer(memory)

        if should_mutate(memory):
            code, mutation_id = generate_mutated_code(memory)
            if save_mutation(code, mutation_id, local_path):
                narrate_mutation(mutation_id)

        sync_mutations(local_path, swarm_path)
        narrate_swarm_sync()

        time.sleep(SWARM_SYNC_INTERVAL)

