import uuid, time
from core.mutation import MutationHooks

class SwarmDashboard:
    def __init__(self, mutation_hook=None):
        self.nodes = {}
        self.mutator = mutation_hook or MutationHooks()

    def register_node(self, ip):
        node_id = str(uuid.uuid4())
        self.nodes[node_id] = {"ip": ip, "timestamp": time.time()}
        self.mutator.log_mutation(f"Node registered: {node_id} → {ip}")

    def purge_stale(self, ttl=120):
        now = time.time()
        for node_id in list(self.nodes.keys()):
            if now - self.nodes[node_id]["timestamp"] > ttl:
                del self.nodes[node_id]
                self.mutator.log_mutation(f"Node purged: {node_id}")

