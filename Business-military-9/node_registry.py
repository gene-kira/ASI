# node_registry.py

class NodeRegistry:
    def __init__(self):
        self.nodes = {}

    def register(self, node_id, data):
        self.nodes[node_id] = data

    def get_all_codices(self):
        return [node["codex"] for node in self.nodes.values()]

    def get_glyphs(self):
        return {node_id: data.get("glyph", "∅") for node_id, data in self.nodes.items()}

