from datetime import datetime

class MutationHooks:
    def __init__(self):
        self.mutations = []

    def log_mutation(self, event):
        self.mutations.append({
            "event": event,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_log(self):
        return self.mutations

