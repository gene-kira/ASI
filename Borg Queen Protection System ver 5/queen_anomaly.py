# queen_anomaly.py
import numpy as np
from sklearn.ensemble import IsolationForest
import random

class AnomalyDetector:
    def __init__(self):
        self.model = IsolationForest(n_estimators=100, contamination=0.05)
        self.audit_log = []
        self.particle_fx = []

    def train(self, data):
        self.model.fit(data)
        self.audit_log.append("glyph(train:telemetry)")

    def detect(self, new_data):
        preds = self.model.predict(new_data)
        anomalies = np.where(preds == -1)[0]
        for i in anomalies:
            fx = self.trigger_particle_fx(i)
            self.particle_fx.append(fx)
            self.audit_log.append(f"glyph(anomaly:{i})")
        return anomalies.tolist()

    def trigger_particle_fx(self, index):
        fx = {
            "id": index,
            "burst": random.choice(["flare", "shockwave", "ripple", "glow"]),
            "color": random.choice(["red", "violet", "cyan", "gold"]),
            "intensity": random.randint(5, 20)
        }
        return fx

    def get_recent_fx(self):
        return self.particle_fx[-5:]

    def get_audit_log(self):
        return self.audit_log[-5:]

