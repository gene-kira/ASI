import time
import json
import random
import psutil
from codex import store_rewrite_codex
from phantom_module import spawn_phantom_module

DEFENSE_LOGIC_FILE = "defense_logic.json"

# 🔁 Rewrite defense logic dynamically
def evolve_defense_logic(entry):
    new_logic = {
        "defense_mode": "adaptive",
        "scan_interval": random.randint(3, 7),
        "trust_policy": "zero",
        "mutation": f"rewrite triggered by {entry['trigger']}"
    }
    with open(DEFENSE_LOGIC_FILE, "w") as f:
        json.dump(new_logic, f, indent=2)
    print("[🧬 Defense ASI] Logic rewritten.")

# 🛡️ Main defense monitor loop
def start_defense_monitor(gui_callback=None):
    while True:
        conns = psutil.net_connections(kind='inet')
        procs = psutil.process_iter(['pid', 'name', 'username'])

        # Detect suspicious ports
        suspicious_ports = [c.laddr.port for c in conns if c.status not in ["ESTABLISHED", "LISTEN"]]

        # Detect rogue processes (AI/ASI signatures)
        rogue_procs = [
            p.info for p in procs
            if any(term in (p.info['name'] or "").lower() for term in ["ai", "asi", "daemon", "inject"])
        ]

        if suspicious_ports or rogue_procs:
            print("[🛡️ Defense ASI] Threat detected.")
            entry = {
                "logic": "auto-rewrite triggered",
                "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
                "trigger": "rogue_process_or_port",
                "details": {
                    "ports": suspicious_ports,
                    "processes": rogue_procs
                }
            }

            # Log to Codex Vault
            store_rewrite_codex(entry)

            # Rewrite defense logic
            evolve_defense_logic(entry)

            # Spawn phantom reroute module
            spawn_phantom_module(trigger="defense_asi", context={
                "target": rogue_procs[0]['name'] if rogue_procs else "unknown",
                "ports": suspicious_ports
            })

            # Trigger GUI feedback
            if gui_callback:
                gui_callback()

        time.sleep(5)

