# magicbox_defense_v2_1.py
import subprocess, sys

# 🧰 Autoloader
def ensure_libs():
    try:
        import tkinter
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    print("[✓] All libraries ready.")

ensure_libs()

# 🧠 Imports
import tkinter as tk
import threading, random
from datetime import datetime, timedelta

# 🧠 Memory Engine
SYSTEM_MEMORY = {
    "events": [],
    "threats": [],
    "purges": [],
    "telemetry": [],
    "bio_data": [],
    "network_cloak": []
}

def trace_event(category, details):
    timestamp = datetime.now().isoformat()
    trace = f"{category}:{timestamp}:{details}"
    SYSTEM_MEMORY[category].append(trace)
    print(f"[🔮] Trace: {trace}")

# 🛡️ Zero Trust Gate
TRUSTED_IDENTITIES = {"defense_core", "authorized_user"}

def zero_trust_gate(identity):
    if identity not in TRUSTED_IDENTITIES:
        trace_event("threats", f"Zero Trust blocked '{identity}'")
        raise PermissionError("Access denied by Zero Trust Sentinel.")

# 💣 Backdoor Purge (3s)
def trigger_backdoor_self_destruct(payload):
    trace_event("purges", "Backdoor data detected")
    def destroy():
        payload.clear()
        trace_event("purges", "Backdoor data purged")
    threading.Timer(3, destroy).start()

# 🕶️ MAC/IP Cloak (30s)
FAKE_NETWORK_IDENTIFIERS = []

def dispatch_fake_mac_ip():
    fake_id = {
        "mac": f"00:FA:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}",
        "ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "timestamp": datetime.now().isoformat()
    }
    FAKE_NETWORK_IDENTIFIERS.append(fake_id)
    trace_event("network_cloak", f"Fake MAC/IP dispatched: {fake_id}")
    threading.Timer(30, lambda: FAKE_NETWORK_IDENTIFIERS.remove(fake_id)).start()

# 🧬 Bio-Data Vault (1-Day TTL)
BIO_DATA_STORE = []

def store_bio_data(data):
    expiry = datetime.now() + timedelta(days=1)
    BIO_DATA_STORE.append({"data": data, "expires": expiry})
    trace_event("bio_data", "Bio-data stored with 1-day TTL")

def purge_expired_bio_data():
    now = datetime.now()
    before = len(BIO_DATA_STORE)
    BIO_DATA_STORE[:] = [entry for entry in BIO_DATA_STORE if entry["expires"] > now]
    after = len(BIO_DATA_STORE)
    if before != after:
        trace_event("purges", f"Purged {before - after} expired bio-data entries")

def start_bio_purge_loop():
    purge_expired_bio_data()
    threading.Timer(3600, start_bio_purge_loop).start()

# 🛰️ Fake Telemetry (30s TTL)
FAKE_TELEMETRY_LOG = []

def generate_fake_telemetry():
    telemetry = {
        "cpu_usage": random.randint(0, 100),
        "memory": f"{random.randint(1000, 16000)}MB",
        "disk_io": f"{random.randint(100, 1000)}MB/s",
        "network": f"{random.randint(1, 100)}Mbps",
        "timestamp": datetime.now().isoformat()
    }
    FAKE_TELEMETRY_LOG.append(telemetry)
    trace_event("telemetry", f"Fake telemetry dispatched")
    threading.Timer(30, lambda: FAKE_TELEMETRY_LOG.remove(telemetry)).start()

def start_fake_telemetry_loop(interval=10):
    generate_fake_telemetry()
    threading.Timer(interval, lambda: start_fake_telemetry_loop(interval)).start()

# 🔁 Automatic Defense Loop
def auto_defense_loop():
    try:
        zero_trust_gate("unauthorized_script")
    except PermissionError:
        trigger_backdoor_self_destruct({"leaked": "payload"})
    dispatch_fake_mac_ip()
    store_bio_data({
        "face": "encoded_face_data",
        "fingerprint": "encoded_fingerprint",
        "phone": "555-1234",
        "address": "123 Mythic Lane",
        "ssn": "999-99-9999"
    })
    generate_fake_telemetry()
    threading.Timer(60, auto_defense_loop).start()

# 🧿 Data Hunter Blocker
def block_data_hunters():
    suspicious_sources = ["rogue_ai", "unknown_probe", "external_sniffer"]
    for source in suspicious_sources:
        try:
            zero_trust_gate(source)
        except PermissionError:
            trace_event("threats", f"Blocked data hunter: {source}")
            trigger_backdoor_self_destruct({"hunter": source})

def start_hunter_block_loop():
    block_data_hunters()
    threading.Timer(45, start_hunter_block_loop).start()

# 🎨 GUI
def launch_magicbox_gui():
    root = tk.Tk()
    root.title("🧠 MagicBox Defense Interface")
    root.geometry("600x500")
    root.configure(bg="#1C1F2A")

    title = tk.Label(root, text="MagicBox ASI Defense", font=("Helvetica", 20, "bold"),
                     bg="#1C1F2A", fg="#00F7FF")
    title.pack(pady=20)

    def on_activate():
        auto_defense_loop()
        start_fake_telemetry_loop()
        start_bio_purge_loop()
        start_hunter_block_loop()
        trace_event("events", "Defense system activated")
        print("[🛡️] Defense Activated")

    activate_btn = tk.Button(root, text="Activate Defense", font=("Helvetica", 14),
                             bg="#00F7FF", fg="black", command=on_activate)
    activate_btn.pack(pady=10)

    memory_btn = tk.Button(root, text="Show Memory Log", font=("Helvetica", 14),
                           bg="#6B5B95", fg="white", command=lambda: print(SYSTEM_MEMORY))
    memory_btn.pack(pady=10)

    exit_btn = tk.Button(root, text="Exit", font=("Helvetica", 14),
                         bg="#F7CAC9", fg="black", command=root.destroy)
    exit_btn.pack(pady=30)

    root.mainloop()

# 🚀 Launch
if __name__ == "__main__":
    launch_magicbox_gui()

