class BioDataSentinel:
    def scan(self, payload):
        keywords = ["face", "finger", "phone", "address", "license", "social"]
        return any(k in payload.lower() for k in keywords)

