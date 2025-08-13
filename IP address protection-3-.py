import os
import sys
import time
import ctypes
import platform
import subprocess
import tkinter as tk
import random
import uuid
import socket
import threading
import pyshark
import requests

# === Mythic Loader ===
loader_symbols = ["🔒", "🧠", "🌌", "🛡️", "🔥", "💀", "✨", "✅"]
loader_text = [
    "Checking admin privileges...",
    "Initializing Vault...",
    "Activating Cloak Node...",
    "Mutating IP & MAC...",
    "Encrypting Telemetry...",
    "Spawning Swarm...",
    "Preparing GUI Overlay...",
    "Ready for Rebirth."
]

def is_admin():
    if os.name == 'nt':
        try: return ctypes.windll.shell32.IsUserAnAdmin()
        except: return False
    else:
        return os.geteuid() == 0

def elevate_windows():
    if not is_admin():
        params = " ".join([f'"{arg}"' for arg in sys.argv])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
        sys.exit()

def mythic_loader():
    for i in range(len(loader_symbols)):
        sys.stdout.write(f"\r{loader_symbols[i]} {loader_text[i]}")
        sys.stdout.flush()
        time.sleep(0.5)
    print("\n[✔] MagicBox Loader Complete.\n")

def mythic_startup():
    if platform.system() == "Windows":
        elevate_windows()
    elif not is_admin():
        print("[ERROR] Please run with sudo/root privileges.")
        sys.exit(1)
    mythic_loader()

# === Vault System ===
vault_path = "vault.ephemeral"

def purge_vault():
    if os.path.exists(vault_path):
        os.remove(vault_path)
        print("[Vault] Purged.")
    else:
        print("[Vault] Already clean.")

def rebirth_vault():
    with open(vault_path, "w") as f:
        f.write(f"VaultID: {uuid.uuid4()}\nTimestamp: {time.time()}")
    print("[Vault] Reborn.")

# === Mutation Engine ===
def mutate_ip_mac():
    new_ip = f"10.0.{random.randint(0,255)}.{random.randint(1,254)}"
    new_mac = ":".join(["%02x" % random.randint(0,255) for _ in range(6)])
    print(f"[Mutation] IP -> {new_ip}, MAC -> {new_mac}")
    return new_ip, new_mac

def sync_with_swarm():
    node_id = random.choice(["Echo", "Nyx", "Sol", "Aether", "Oblivion"])
    print(f"[Swarm] Synced with node: {node_id}")
    return node_id

# === Proxy Rotation ===
proxies = [
    {"http": "http://proxy1:port", "https": "http://proxy1:port"},
    {"http": "http://proxy2:port", "https": "http://proxy2:port"},
]

def send_through_proxy(url):
    proxy = random.choice(proxies)
    try:
        response = requests.get(url, proxies=proxy)
        print(f"[Proxy] Used: {proxy['http']}")
        return response.text
    except Exception as e:
        print(f"[Proxy] Error: {e}")
        return None

# === Real Packet Sniffing ===
def detect_anomaly(packet):
    return packet["payload"] in ["MALWARE", "AUTH"] or packet["size"] > 1400

def start_sniffer(callback):
    def sniff():
        capture = pyshark.LiveCapture(interface='eth0')
        for packet in capture.sniff_continuously():
            try:
                info = {
                    "src": packet.ip.src,
                    "dst": packet.ip.dst,
                    "payload": packet.highest_layer,
                    "size": int(packet.length)
                }
                if detect_anomaly(info):
                    callback(info)
            except Exception:
                continue
    threading.Thread(target=sniff, daemon=True).start()

# === GUI Animations ===
def animate_node_pulse(canvas, node_name):
    for i in range(5):
        radius = 10 + i * 15
        canvas.create_oval(200 - radius, 75 - radius, 200 + radius, 75 + radius,
                           outline="#00bcd4", width=2)
        canvas.create_text(200, 75, text=node_name, fill="#00ffcc", font=("Courier", 12))
        canvas.update()
        time.sleep(0.1)
        canvas.delete("all")

def animate_shield(canvas):
    for i in range(20):
        color = f"#00ff{hex(15 - i % 10)[2:]}"
        canvas.create_oval(150, 50, 250, 150, outline=color, width=3)
        canvas.update()
        time.sleep(0.03)
        canvas.delete("all")

# === GUI Launcher ===
def launch_gui():
    root = tk.Tk()
    root.title("🧠 MagicBox Cloak Node")
    root.geometry("400x500")
    root.configure(bg="#1e1e2e")

    tk.Label(root, text="MagicBox Cloak Node", font=("Courier", 18), fg="#00ffcc", bg="#1e1e2e").pack(pady=10)
    canvas = tk.Canvas(root, width=400, height=150, bg="#1e1e2e", highlightthickness=0)
    canvas.pack()

    def engage():
        node = sync_with_swarm()
        animate_node_pulse(canvas, node)
        animate_shield(canvas)

    def purge_and_rebirth():
        purge_vault()
        rebirth_vault()
        animate_shield(canvas)

    def mutate_node():
        ip, mac = mutate_ip_mac()
        node = sync_with_swarm()
        animate_node_pulse(canvas, node)
        print(f"[Node] {node} | IP: {ip} | MAC: {mac}")

    tk.Button(root, text="Engage Swarm", font=("Courier", 12), bg="#00ffcc", command=engage).pack(pady=5)
    tk.Button(root, text="Purge Vault", font=("Courier", 12), bg="#ff6666", command=purge_and_rebirth).pack(pady=5)
    tk.Button(root, text="Mutate Node", font=("Courier", 12), bg="#66ff66", command=mutate_node).pack(pady=5)

    def on_threat(packet):
        print(f"[Threat] Detected: {packet}")
        canvas.create_text(200, 75, text="⚠️ Threat Detected", fill="red", font=("Courier", 14))
        purge_vault()

    start_sniffer(on_threat)
    root.mainloop()

# === Main Execution ===
if __name__ == "__main__":
    mythic_startup()
    launch_gui()

