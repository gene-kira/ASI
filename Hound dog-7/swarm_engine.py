import random
import time
import threading

# 🧠 Swarm Node Registry
swarm_nodes = ["Node-A", "Node-B", "Node-C", "Node-D", "Node-E"]

# 🕸️ Hive Sync Pulse
def hive_sync_pulse(mutation_output=None):
    node = random.choice(swarm_nodes)
    msg = f"🕸️ Hive sync pulse from {node} — threat logic updated\n"
    if mutation_output:
        mutation_output.insert("end", msg)
    print(f"[Hive Sync] {msg.strip()}")

# 🧠 Swarm Coordination Loop
def start_swarm_sync(mutation_output):
    def loop():
        while True:
            hive_sync_pulse(mutation_output)
            time.sleep(random.randint(20, 40))  # Randomized sync interval
    threading.Thread(target=loop, daemon=True).start()

