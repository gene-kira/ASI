class AIThreatModel:
    @staticmethod
    def evaluate(features):
        if not features or "live" not in features:
            raise ValueError("Non-live features rejected")
        return 0.91 if "anomaly" in features or "ASI" in features else 0.99

