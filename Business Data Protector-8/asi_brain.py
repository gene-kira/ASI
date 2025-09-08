# asi_brain.py

import time, random, platform, subprocess
import numpy as np
from sklearn.ensemble import IsolationForest
from utils import log_codex

class ASIBrain:
    def __init__(self, memory):
        self.memory = memory
        self.codex = []
        self.threat_score = 0
        self.model = IsolationForest(n_estimators=100, contamination=0.05)
        self.last_mutation = time.time()

    def train_model(self, samples):
        self.model.fit(np.array(samples))
        log_codex("🧠 ASI model trained")

    def detect_anomaly(self, sample):
        return self.model.predict([sample])[0] == -1

    def analyze_traffic(self, ip, country, sent, recv):
        score = 0
        if country in ["Russia", "China", "North Korea", "Iran"]: score += 5
        if recv > 500 or sent > 500: score += 3
        if ip.startswith("127.") or ip.startswith("10."): score -= 2
        self.threat_score += score
        if score >= 5 or self.detect_anomaly([sent, recv]):
            self.trigger_defense(ip, country)

    def trigger_defense(self, ip, country):
        self.codex.append({
            "timestamp": time.strftime("%H:%M:%S"),
            "label": f"Blocked {ip}",
            "source": f"Geo: {country}"
        })
        self.block_ip(ip)

    def block_ip(self, ip):
        try:
            if platform.system() == "Linux":
                subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
            elif platform.system() == "Windows":
                cmd = f'New-NetFirewallRule -DisplayName "ASIBlock" -Direction Inbound -RemoteAddress {ip} -Action Block'
                subprocess.run(["powershell", "-Command", cmd])
        except Exception as e:
            log_codex(f"❌ Firewall block failed: {e}")

    def mutate_codex(self):
        if time.time() - self.last_mutation > 60:
            mutation = random.choice(["Elevate", "Decoy", "Lockdown", "Mirror"])
            self.last_mutation = time.time()
            self.codex.append({
                "timestamp": time.strftime("%H:%M:%S"),
                "label": f"Codex Mutation → {mutation}",
                "source": "ASI Brain"
            })

    def sync_with_swarm(self, nodes):
        for node in nodes:
            self.codex.append({
                "timestamp": time.strftime("%H:%M:%S"),
                "label": f"Synced with {node}",
                "source": "Swarm Sync"
            })

    def export_codex(self):
        return self.codex[-50:]

