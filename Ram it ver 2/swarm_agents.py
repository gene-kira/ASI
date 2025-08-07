class CacheAgent:
    def __init__(self, id, size_mb):
        self.id = id
        self.size_mb = size_mb
        self.status = "Idle"
        self.history = []

    def rebalance(self, pressure):
        self.history.append((self.size_mb, pressure))
        if pressure > 0.8:
            self.size_mb *= 0.9
            self.status = "Purging"
        else:
            self.status = "Stable"

def spawn_agents(total_size, count):
    segment = total_size // count
    return [CacheAgent(i, segment) for i in range(count)]

