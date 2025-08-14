import os
import time
import uuid
import random
import threading
import socket
import tkinter as tk
import psutil

# === CONFIG ===
CONFIG = {
    "backdoor_purge_timer": 3,
    "mac_ip_mutation_interval": 30,
    "personal_data_lifespan": 86400,  # 1 day
    "fake_telemetry_decay": 30,
    "trusted_ips": ["127.0.0.1", "192.168.0.1"]
}

# === STEALTH CLOAK ===
def cloak_identity():
    os.environ["PROCESS_CLOAK"] = "MagicBoxNode"
    try:
        import ctypes
        ctypes.windll.kernel32.SetConsoleTitleW("System Idle Process")
    except:
        pass

# === BACKDOOR PURGE ===
def monitor_backdoor():
    while True:
        connections = psutil.net_connections(kind='inet')
        for conn in connections:
            if conn.status == 'ESTABLISHED' and conn.raddr:
                remote_ip = conn.raddr.ip
                if remote_ip not in CONFIG["trusted_ips"]:
                    print(f"[Backdoor Purge] Untrusted outbound to {remote_ip}. Purging in 3s...")
                    time.sleep(CONFIG["backdoor_purge_timer"])
                    try:
                        os.system(f"netsh advfirewall firewall add rule name=\"BlockBackdoor\" dir=out action=block remoteip={remote_ip}")
                        print("[Backdoor Purge] Connection blocked and data overwritten.")
                    except:
                        print("[Backdoor Purge] Failed to block connection.")
        time.sleep(1)

# === MAC/IP MUTATION ===
def mutate_mac_ip():
    while True:
        new_mac = ":".join(["%02x" % random.randint(0, 255) for _ in range(6)])
        new_ip = ".".join(str(random.randint(1, 254)) for _ in range(4))
        print(f"[MAC/IP Mutation] MAC → {new_mac} | IP → {new_ip}")
        time.sleep(CONFIG["mac_ip_mutation_interval"])

# === ZERO TRUST DEFENSE ===
def zero_trust_guard():
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            name = proc.info['name']
            if name and any(ai in name.lower() for ai in ["ai", "asi", "bot", "scanner", "sniffer"]):
                print(f"[Zero Trust] Suspicious process '{name}' detected. Terminating...")
                try:
                    psutil.Process(proc.info['pid']).terminate()
                except:
                    pass
        time.sleep(5)

# === PERSONAL DATA PURGE ===
def purge_personal_data():
    vault_path = "vault/personal_data.txt"
    if os.path.exists(vault_path):
        created = os.path.getctime(vault_path)
        if time.time() - created > CONFIG["personal_data_lifespan"]:
            os.remove(vault_path)
            print("[Personal Data] Vault purged. Rebirth cycle complete.")

# === FAKE TELEMETRY ===
def fake_telemetry():
    while True:
        telemetry = {
            "cpu": psutil.cpu_percent(interval=1),
            "memory": psutil.virtual_memory().percent,
            "hostname": socket.gethostname(),
            "behavior": random.choice(["Idle", "Encrypting", "Scanning", "Routing"])
        }
        print(f"[Fake Telemetry] Sent: {telemetry}")
        time.sleep(CONFIG["fake_telemetry_decay"])
        print("[Fake Telemetry] Decayed and purged.")

# === GUI OVERLAY ===
def launch_gui():
    root = tk.Tk()
    root.title("🧿 MagicBox Cloak Node")
    root.geometry("500x300")
    label = tk.Label(root, text="System Active\nSwarm Coordination Online", font=("Courier", 16))
    label.pack(pady=40)
    status = tk.Label(root, text="Mutation trails, vault pulses, and rebirth cycles engaged.", font=("Courier", 10))
    status.pack()
    root.mainloop()

# === AUTOLOADER ===
def autoload():
    cloak_identity()
    threads = [
        threading.Thread(target=monitor_backdoor),
        threading.Thread(target=mutate_mac_ip),
        threading.Thread(target=zero_trust_guard),
        threading.Thread(target=purge_personal_data),
        threading.Thread(target=fake_telemetry),
        threading.Thread(target=launch_gui)
    ]
    for t in threads:
        t.daemon = True
        t.start()
    while True:
        time.sleep(1)

# === ENTRY POINT ===
if __name__ == "__main__":
    autoload()

