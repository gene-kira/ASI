import time

class DataDestructionEngine:
    def __init__(self, narrator):
        self.tracked = {}
        self.narrator = narrator

    def track(self, data_id, category):
        self.tracked[data_id] = {"category": category, "timestamp": time.time()}

    def enforce(self):
        now = time.time()
        for data_id, meta in list(self.tracked.items()):
            elapsed = now - meta["timestamp"]
            if meta["category"] == "backdoor" and elapsed > 3:
                self.destroy(data_id)
            elif meta["category"] == "mac_ip" and elapsed > 30:
                self.destroy(data_id)
            elif meta["category"] == "bio" and elapsed > 86400:
                self.destroy(data_id)
            elif meta["category"] == "telemetry" and elapsed > 30:
                self.destroy(data_id)

    def destroy(self, data_id):
        self.narrator.warn(f"Self-destruct triggered for {data_id}")
        del self.tracked[data_id]

