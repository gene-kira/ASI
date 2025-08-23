import threading
import time
import random
from config import MAGICBOX_COLORS
from voice import speak

# 🧬 Personal Data Store
personal_data_store = []

# 🧠 Swarm Node Registry
swarm_nodes = ["Node-A", "Node-B", "Node-C", "Node-D"]

# 💣 Backdoor Self-Destruct
def schedule_backdoor_self_destruct(data_packet, mutation_output=None):
    def destroy():
        if mutation_output:
            mutation_output.insert("end", f"💣 Backdoor data self-destructed: {data_packet}\n")
        print(f"[Self-Destruct] Backdoor data purged: {data_packet}")
    threading.Timer(3, destroy).start()

# 💣 MAC/IP Self-Destruct
def schedule_mac_ip_self_destruct(identifier, mutation_output=None):
    def destroy():
        if mutation_output:
            mutation_output.insert("end", f"💣 MAC/IP self-destructed: {identifier}\n")
        print(f"[Self-Destruct] MAC/IP purged: {identifier}")
    threading.Timer(30, destroy).start()

# 🧬 Zero Trust Enforcement
def is_trusted(entity_id):
    return False

def verify_action(entity_id, action, mutation_output=None):
    if not is_trusted(entity_id):
        msg = f"🚫 Blocked unverified action from {entity_id}\n"
        if mutation_output:
            mutation_output.insert("end", msg)
        print(f"[Zero Trust] {msg.strip()}")
        return False
    return True

# 🧬 Personal Data Expiry
def tag_personal_data(data):
    expiry = time.time() + 86400
    personal_data_store.append({"data": data, "expires": expiry})
    print(f"[Tagged] Personal data scheduled for purge: {data}")

def purge_expired_personal_data(mutation_output=None):
    now = time.time()
    before = len(personal_data_store)
    personal_data_store[:] = [d for d in personal_data_store if d["expires"] > now]
    purged = before - len(personal_data_store)
    if purged > 0 and mutation_output:
        mutation_output.insert("end", f"💣 Purged {purged} expired personal data entries\n")

# 🕵️ Fake Telemetry Generator
def generate_fake_telemetry(mutation_output=None):
    fake = {
        "cpu": random.randint(1, 100),
        "location": "Null Island",
        "mac": "00:00:00:00:00:00",
        "ip": "0.0.0.0"
    }
    if mutation_output:
        mutation_output.insert("end", f"🕵️ Fake telemetry sent: {fake}\n")
    print(f"[Fake Telemetry] Sent: {fake}")

    def destroy():
        if mutation_output:
            mutation_output.insert("end", "💣 Fake telemetry self-destructed\n")
        print("[Fake Telemetry] Self-destructed")

    threading.Timer(30, destroy).start()

# 🕸️ Swarm Sync Pulse
def swarm_sync_pulse(mutation_output=None):
    node = random.choice(swarm_nodes)
    msg = f"🕸️ Swarm sync pulse from {node}\n"
    if mutation_output:
        mutation_output.insert("end", msg)
    print(f"[Swarm Sync] {msg.strip()}")

# 🧠 Defense Scheduler
def start_defense_scheduler(mutation_output):
    def loop():
        while True:
            purge_expired_personal_data(mutation_output)
            generate_fake_telemetry(mutation_output)
            swarm_sync_pulse(mutation_output)
            time.sleep(30)

    threading.Thread(target=loop, daemon=True).start()

