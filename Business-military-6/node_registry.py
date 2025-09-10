# node_registry.py

class NodeRegistry:
    def __init__(self):
        self.nodes = {}

    def register(self, node_id, codex_snapshot):
        self.nodes[node_id] = codex_snapshot

    def get_all_codices(self):
        return [node["codex"] for node in self.nodes.values()]

    def broadcast_codex(self, source_id, codex):
        for node_id in self.nodes:
            if node_id != source_id:
                self.nodes[node_id]["codex"].update(codex)

