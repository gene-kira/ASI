class ZeroTrustEnforcer:
    def __init__(self, rules):
        self.rules = rules

    def validate_access(self, process_name):
        return process_name in self.rules.get("allowed_processes", [])

