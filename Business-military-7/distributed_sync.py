# distributed_sync.py

class DistributedSyncBus:
    def __init__(self, node_id, codex_mutator, registry):
        self.node_id = node_id
        self.codex = codex_mutator
        self.registry = registry

    def sync(self):
        snapshot = self.codex.export_codex()
        self.registry.register(self.node_id, {"codex": snapshot})
        for other_codex in self.registry.get_all_codices():
            self.codex.sync_with(other_codex)
        return f"[SYNC] {self.node_id} synced with swarm"

