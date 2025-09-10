class MythicNode:
    def __init__(self, node_id, whitelisted=True):
        self.node_id = node_id
        self.whitelisted = whitelisted

    def receive_encrypted(self, payload):
        print(f"[{self.node_id}] Received encrypted sync.")

    def receive_persona_memory(self, payload):
        print(f"[{self.node_id}] Synced persona memory.")

