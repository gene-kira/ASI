# anomaly_profiler.py
import torch
import torch.nn as nn
import torch.nn.functional as F
import random

class AnomalyProfiler(nn.Module):
    def __init__(self):
        super(AnomalyProfiler, self).__init__()
        self.fc1 = nn.Linear(10, 32)
        self.fc2 = nn.Linear(32, 16)
        self.fc3 = nn.Linear(16, 1)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.to(self.device)

    def forward(self, x):
        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))
        return torch.sigmoid(self.fc3(x))

    def score_agent(self, telemetry):
        # telemetry: list of 10 normalized features
        x = torch.tensor(telemetry, dtype=torch.float32).to(self.device)
        with torch.no_grad():
            score = self.forward(x).item()
        return score

    def generate_fake_telemetry(self):
        # Simulate agent behavior: access rate, mutation freq, purge history, etc.
        return [random.uniform(0, 1) for _ in range(10)]

    def batch_score(self, agents):
        results = {}
        for agent in agents:
            telemetry = self.generate_fake_telemetry()
            score = self.score_agent(telemetry)
            results[agent] = score
        return results

