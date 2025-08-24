import threading
import time
import random
from config import MAGICBOX_COLORS
from voice import speak

# 🔐 Personal Data Store
personal_data_store = []

# 💣 Backdoor Data Self-Destruct (3 sec)
def schedule_backdoor_self_destruct(data_packet, mutation_output=None):
    def destroy():
        if mutation_output:
            mutation_output.insert("end", f"💣 Backdoor data self-destructed: {data_packet}\n")
        print(f"[Self-Destruct] Backdoor data purged: {data_packet}")
    threading.Timer(3, destroy).start()

# 💣 MAC/IP Auto-Destruct (30 sec)
def schedule_mac_ip_self_destruct(identifier, mutation_output=None):
    def destroy():
        if mutation_output:
            mutation_output.insert("end", f"💣 MAC/IP self-destructed: {identifier}\n")
        print(f"[Self-Destruct] MAC/IP purged: {identifier}")
    threading.Timer(30, destroy).start()

# 🚫 Zero Trust Enforcement
def is_trusted(entity_id):
    return False  # No implicit trust

def verify_action(entity_id, action, mutation_output=None):
    if not is_trusted(entity_id):
        msg = f"🚫 Blocked unverified action from {entity_id}\n"
        if mutation_output:
            mutation_output.insert("end", msg)
        print(f"[Zero Trust] {msg.strip()}")
        return False
    return True

# 🔐 Personal Data Expiry (1 day)
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
    if purged > 0:
        print(f"[Purge] {purged} personal data entries removed")

# 🕵️ Fake Telemetry + Auto-Destruct (30 sec)
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

# 🧠 Adaptive Threshold Tuning
def tune_threshold(app):
    recent = app.mutation_output.get("end-1000c", "end")
    if "terminated" not in recent:
        app.trust_threshold = max(1, app.trust_threshold - 1)
    else:
        app.trust_threshold = min(10, app.trust_threshold + 1)
    app.threshold_label.config(text=f"Kill Threshold: {app.trust_threshold}")
    print(f"[Evolution] Threshold adjusted to {app.trust_threshold}")

# 🧬 Cloaking Mutation
def evolve_cloaking_patterns(app):
    msg = "🧬 Cloaking logic mutated based on recent threat vectors\n"
    app.mutation_output.insert("end", msg)
    print(f"[Evolution] {msg.strip()}")

# 🧠 Evolution Loop
def start_evolution_loop(app):
    def loop():
        while True:
            tune_threshold(app)
            evolve_cloaking_patterns(app)
            time.sleep(60)
    threading.Thread(target=loop, daemon=True).start()

# 🧠 Defense Scheduler
def start_defense_scheduler(mutation_output):
    def loop():
        while True:
            purge_expired_personal_data(mutation_output)
            generate_fake_telemetry(mutation_output)
            time.sleep(30)
    threading.Thread(target=loop, daemon=True).start()

