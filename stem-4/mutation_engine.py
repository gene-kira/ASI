import time
import random
import psutil
from codex import store_rewrite_codex

class Pulse:
    def __init__(self, port, entropy):
        self.port = port
        self.entropy = entropy

def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    avg_entropy = sum(p.entropy for p in recent) / len(recent)
    variance = max(p.entropy for p in recent) - min(p.entropy for p in recent)
    return variance > 2.5 and avg_entropy > 7.0

def initiate_mutation_vote(pulse):
    votes = [random.choice(["yes", "no"]) for _ in range(5)]
    return votes.count("yes") >= 3

def rewrite_optimization_logic(trigger="symbolic_density_spike"):
    new_threshold = random.randint(6, 8)
    print(f"[🧠 Rewrite] New cloaking threshold: {new_threshold}")
    return {
        "logic": f"entropy > {new_threshold}",
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "trigger": trigger,
        "consensus": "mutation_vote_passed"
    }

def scan_live_flows():
    flows = []
    conns = psutil.net_connections(kind='inet')
    for conn in conns:
        try:
            laddr = conn.laddr.port
            raddr = conn.raddr.port if conn.raddr else 0
            status = conn.status
            proto = "TCP" if conn.type == psutil.SOCK_STREAM else "UDP"
            entropy = (
                abs(laddr - raddr) / 100 +
                (1 if status not in ["ESTABLISHED", "LISTEN"] else 0) +
                (1.5 if proto == "UDP" else 1)
            )
            flows.append(Pulse(port=laddr, entropy=entropy))
        except Exception:
            continue
    return flows

def start_mutation_monitor(gui_callback=None):
    flows = []
    while True:
        new_flows = scan_live_flows()
        flows.extend(new_flows)
        flows = flows[-50:]
        if detect_density_spike(flows):
            pulse = new_flows[-1]
            if initiate_mutation_vote(pulse):
                entry = rewrite_optimization_logic()
                store_rewrite_codex(entry)
                print("[🜂 Mutation] Codex updated.")
                if gui_callback:
                    gui_callback()
        time.sleep(3)

