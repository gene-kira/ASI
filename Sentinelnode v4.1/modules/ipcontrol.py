class IPAccessControl:
    def __init__(self, narrator):
        self.allow_list = set(["10.0.0.5", "192.168.1.100"])
        self.block_list = set(["66.66.66.66", "203.0.113.0"])
        self.narrator = narrator

    def evaluate(self, ip):
        if ip in self.block_list:
            self.narrator.warn(f"Blocked IP {ip} rejected")
            return "block"
        if ip not in self.allow_list:
            self.narrator.warn(f"IP {ip} not in allow list")
            return "reject"
        self.narrator.log(f"IP {ip} allowed")
        return "allow"

