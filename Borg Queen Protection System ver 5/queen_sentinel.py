# queen_sentinel.py
import random, time

class SwarmSentinel:
    def __init__(self):
        self.agents = {}
        self.audit_log = []
        selffx = []

    def deploy_agent(self, agent_id, target):
        agent = {
            "id": agent_id,
            "target": target,
            "status": "active",
            "deployed_at": time.time()
        }
        self.agents[agent_id] = agent
        self.audit_log.append(f"glyph(agent:deploy:{agent_id})")
        return agent

    def neutralize_threat(self, agent_id):
        if agent_id not in self.agents:
            raise Exception("Agent not found")
        agent = self.agents[agent_id]
        agent["status"] = "neutralized"
        fx = self.trigger_particle_fx(agent["target"])
        selffx.append(fx)
        self.audit_log.append(f"glyph(agent:neutralize:{agent_id})")
        return fx

    def trigger_particle_fx(self, target):
        return {
            "target": target,
            "burst": random.choice(["shockwave", "flare", "ripple"]),
            "color": random.choice(["red", "cyan", "gold"]),
            "intensity": random.randint(10, 40),
            "timestamp": time.time()
        }

    def get_active_agents(self):
        return {k: v for k, v in self.agents.items() if v["status"] == "active"}

    def get_recent_fx(self):
        return selffx[-5:]

    def get_audit_log(self):
        return self.audit_log[-5:]

