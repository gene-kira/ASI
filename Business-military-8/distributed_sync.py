# distributed_sync.py

from encrypted_sync import EncryptedSync

class DistributedSyncBus:
    def __init__(self, node_id, codex_mutator, registry, secret_key):
        self.node_id = node_id
        self.codex = codex_mutator
        self.registry = registry
        self.crypto = EncryptedSync(node_id, secret_key)

    def sync(self):
        snapshot = self.codex.export_codex()
        encrypted = self.crypto.encrypt_codex(snapshot)
        self.registry.register(self.node_id, {
            "codex": snapshot,
            "encrypted": encrypted,
            "glyph": "∅"
        })

        for node_id, data in self.registry.nodes.items():
            if node_id != self.node_id:
                decrypted = self.crypto.decrypt_codex(data["encrypted"])
                if decrypted:
                    self.codex.sync_with(decrypted["codex"])
        return f"[SYNC] {self.node_id} synced with swarm"

