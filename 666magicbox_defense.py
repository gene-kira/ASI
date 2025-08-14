# magicbox_defense.py
import subprocess, sys

# 🧰 Auto-install required libraries
def ensure_libs():
    try:
        import tkinter
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "tk"])
    print("[✓] All libraries ready.")

ensure_libs()

# 🧠 Defense Logic
import tkinter as tk
import threading, random
from datetime import datetime, timedelta

# Zero Trust
TRUSTED_IDENTITIES = {"defense_core", "authorized_user"}

def zero_trust_gate(identity):
    if identity not in TRUSTED_IDENTITIES:
        print(f"[🚫] Zero Trust Blocked '{identity}'")
        raise PermissionError("Access denied by Zero Trust Sentinel.")

# Backdoor Purge (3s)
def trigger_backdoor_self_destruct(payload):
    print("⚠️] Backdoor data detected. Initiating 3s purge.")
    def destroy():
        payload.clear()
        print("[💥] Backdoor data purged.")
    threading.Timer(3, destroy).start()

# MAC/IP Cloak (30s)
FAKE_NETWORK_IDENTIFIERS = []

def dispatch_fake_mac_ip():
    fake_id = {
        "mac": f"00:FA:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}:{random.randint(10,99):02X}",
        "ip": f"10.{random.randint(0,255)}.{random.randint(0,255)}.{random.randint(0,255)}",
        "timestamp": datetime.now().isoformat()
    }
    FAKE_NETWORK_IDENTIFIERS.append(fake_id)
    print(f"[🕶️] Fake MAC/IP dispatched: {fake_id}")
    threading.Timer(30, lambda: FAKE_NETWORK_IDENTIFIERS.remove(fake_id)).start()

# Bio-Data Vault (1-Day TTL)
BIO_DATA_STORE = []

def store_bio_data(data):
    expiry = datetime.now() + timedelta(days=1)
    BIO_DATA_STORE.append({"data": data, "expires": expiry})
    print("[🧬] Bio-data stored with 1-day TTL.")

def purge_expired_bio_data():
    now = datetime.now()
    before = len(BIO_DATA_STORE)
    BIO_DATA_STORE[:] = [entry for entry in BIO_DATA_STORE if entry["expires"] > now]
    after = len(BIO_DATA_STORE)
    if before != after:
        print(f"[💀] Purged {before - after} expired bio-data entries.")

def start_bio_purge_loop():
    threading.Timer(3600, lambda: [purge_expired_bio_data(), start_bio_purge_loop()]).start()

# Fake Telemetry (30s TTL)
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
    print(f"[🛰️] Fake telemetry dispatched: {telemetry}")
    threading.Timer(30, lambda: FAKE_TELEMETRY_LOG.remove(telemetry)).start()

def start_fake_telemetry_loop(interval=10):
    def loop():
        generate_fake_telemetry()
        threading.Timer(interval, loop).start()
    loop()

# 🎨 Old-Guy-Friendly GUI
def launch_magicbox_gui():
    root = tk.Tk()
    root.title("🧠 MagicBox Defense Interface")
    root.geometry("600x500")
    root.configure(bg="#1C1F2A")

    title = tk.Label(root, text="MagicBox ASI Defense", font=("Helvetica", 20, "bold"),
                     bg="#1C1F2A", fg="#00F7FF")
    title.pack(pady=20)

    def on_activate():
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
        print("[🛡️] Defense Activated")

    activate_btn = tk.Button(root, text="Activate Defense", font=("Helvetica", 14),
                             bg="#00F7FF", fg="black", command=on_activate)
    activate_btn.pack(pady=10)

    telemetry_btn = tk.Button(root, text="Start Fake Telemetry Loop", font=("Helvetica", 14),
                              bg="#6B5B95", fg="white", command=start_fake_telemetry_loop)
    telemetry_btn.pack(pady=10)

    purge_btn = tk.Button(root, text="Start Bio Purge Loop", font=("Helvetica", 14),
                          bg="#FF6F61", fg="white", command=start_bio_purge_loop)
    purge_btn.pack(pady=10)

    exit_btn = tk.Button(root, text="Exit", font=("Helvetica", 14),
                         bg="#F7CAC9", fg="black", command=root.destroy)
    exit_btn.pack(pady=30)

    root.mainloop()

# 🚀 Launch
if __name__ == "__main__":
    launch_magicbox_gui()

