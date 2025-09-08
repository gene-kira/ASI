# asi_brain.py

import time
import random
import platform
import subprocess
import numpy as np
from sklearn.ensemble import IsolationForest
from utils import log_codex
from persona_engine import inject_persona
from deception_engine import trigger_deception_overlay

class ASIBrain:
    def __init__(self, memory):
        self.memory = memory
        self.codex = []
        self.threat_score = 0
        self.persona_state = "Neutral"
        self.last_mutation = time.time()
        self.model = IsolationForest(n_estimators=100, contamination=0.05)
        self.training_data = []

    # 🧠 Train ML model with traffic samples
    def train_model(self, traffic_samples):
        self.training_data = np.array(traffic_samples)
        self.model.fit(self.training_data)
        log_codex("🧠 ASI model trained on traffic samples")

    # 📈 Detect anomaly using ML
    def detect_anomaly(self, sample):
        result = self.model.predict([sample])[0]
        if result == -1:
            self.codex.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "event": f"⚠️ ML anomaly detected: {sample}"
            })
            log_codex(f"⚠️ ML anomaly detected: {sample}")
            return True
        return False

    # 🔍 Analyze traffic and assign threat score
    def analyze_traffic(self, ip, country, sent_kbps, recv_kbps):
        score = 0
        if country in ["Russia", "China", "North Korea", "Iran"]:
            score += 5
        if recv_kbps > 500 or sent_kbps > 500:
            score += 3
        if "127." in ip or ip.startswith("10."):
            score -= 2

        self.threat_score += score
        self.codex.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": f"Analyzed {ip} ({country}) → Score: {score}"
        })

        if score >= 5 or self.detect_anomaly([sent_kbps, recv_kbps]):
            self.trigger_defense(ip, country)

    # 🔥 Trigger defense logic
    def trigger_defense(self, ip, country):
        overlay = "GeoShield" if country else "PulseLock"
        trigger_deception_overlay(overlay)
        persona = inject_persona(self.memory)
        self.persona_state = persona
        log_codex(f"🧠 ASI triggered defense for {ip} from {country} → Persona: {persona}")
        self.codex.append({
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "event": f"Defense triggered → {ip} | {country} | Persona: {persona}"
        })
        self.block_ip(ip)

    # 🔒 Real-time firewall control
    def block_ip(self, ip):
        system = platform.system()
        try:
            if system == "Linux":
                subprocess.run(["iptables", "-A", "INPUT", "-s", ip, "-j", "DROP"])
                log_codex(f"🔥 IP blocked via iptables: {ip}")
            elif system == "Windows":
                cmd = f'New-NetFirewallRule -DisplayName "ASIBlock" -Direction Inbound -RemoteAddress {ip} -Action Block'
                subprocess.run(["powershell", "-Command", cmd])
                log_codex(f"🔥 IP blocked via Windows Firewall: {ip}")
        except Exception as e:
            log_codex(f"❌ Firewall block failed for {ip}: {e}")

    # 🧬 Codex mutation logic
    def mutate_codex(self):
        now = time.time()
        if now - self.last_mutation > 60:
            mutation = random.choice(["Elevate", "Decoy", "Lockdown", "Mirror"])
            self.codex.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "event": f"Codex mutation: {mutation}"
            })
            self.last_mutation = now
            log_codex(f"🧬 Codex mutated → {mutation}")

    # 🔗 Swarm sync logic
    def sync_with_swarm(self, swarm_nodes):
        for node in swarm_nodes:
            self.codex.append({
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
                "event": f"Swarm sync with {node}"
            })
            log_codex(f"🔗 Synced with node: {node}")

    # 📘 Export codex entries
    def export_codex(self):
        return self.codex[-50:]

