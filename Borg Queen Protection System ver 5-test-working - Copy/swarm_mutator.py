# swarm_mutator.py
import time
import random

class SwarmMutator:
    def __init__(self):
        self.agents = {}
        self.mutation_log = []
        self.purge_daemons = []

    def register_agent(self, agent_id, behavior):
        self.agents[agent_id] = {
            "id": agent_id,
            "behavior": behavior,
            "mutations": [],
            "status": "active"
        }

    def mutate_agent(self, agent_id):
        if agent_id not in self.agents:
            return None

        agent = self.agents[agent_id]
        mutation = self.generate_mutation(agent["behavior"])
        agent["behavior"] = mutation
        agent["mutations"].append(mutation)

        log_entry = {
            "agent": agent_id,
            "mutation": mutation,
            "timestamp": time.time()
        }
        self.mutation_log.append(log_entry)
        return log_entry

    def generate_mutation(self, behavior):
        # Simple mutation logic (can evolve later)
        return behavior + "_v" + str(random.randint(1, 999))

    def launch_purge_daemon(self, target):
        daemon = {
            "target": target,
            "status": "purging",
            "timestamp": time.time(),
            "fx": self.trigger_purge_fx(target)
        }
        self.purge_daemons.append(daemon)
        return daemon

    def trigger_purge_fx(self, target):
        return {
            "target": target,
            "burst": random.choice(["flare", "shockwave", "ripple"]),
            "color": random.choice(["magenta", "white", "black"]),
            "intensity": random.randint(20, 60),
            "timestamp": time.time()
        }

    def get_mutation_log(self):
        return self.mutation_log[-5:]

    def get_purge_history(self):
        return self.purge_daemons[-5:]

