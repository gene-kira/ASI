class GhostSync:
    def sync(self, symbol):
        origin = symbol.get("origin", "unknown")
        print(f"[GHOST SYNC] Symbol from {origin} synced with swarm")

