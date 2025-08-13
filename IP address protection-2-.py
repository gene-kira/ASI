# === AUTOLOADER ===
import subprocess
import sys

required = ['psutil', 'pyshark']
for lib in required:
    try:
        __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# === IMPORTS ===
import os
import time
import json
import random
import threading
import psutil
import tkinter as tk
from tkinter import messagebox
import pyshark

# === CONFIG ===
VAULT_PATH = "vault.json"
INTERFACE = "eth0"  # Change to your actual interface
WHITELIST = ["python3", "systemd", "bash"]

# === SAFE SUBPROCESS WRAPPER ===
def safe_run(cmd):
    try:
        subprocess.run(cmd, check=True)
    except Exception as e:
        print(f"[ERROR] Command failed: {cmd} → {e}")

# === PERSONAL DATA VAULT ===
def store_personal_data(data):
    entry = {"data": data, "timestamp": time.time()}
    with open(VAULT_PATH, "a") as f:
        f.write(json.dumps(entry) + "\n")

def purge_old_data():
    try:
        now = time.time()
        if not os.path.exists(VAULT_PATH): return
        with open(VAULT_PATH, "r") as f:
            entries = [json.loads(line) for line in f]
        fresh = [e for e in entries if now - e["timestamp"] < 86400]
        with open(VAULT_PATH, "w") as f:
            for e in fresh:
                f.write(json.dumps(e) + "\n")
        print("[INFO] Vault purged")
    except Exception as e:
        print(f"[ERROR] Vault purge failed: {e}")

# === FAKE TELEMETRY ===
def generate_fake_telemetry():
    return {
        "location": random.choice(["Tokyo", "Berlin", "Mars"]),
        "device_id": hex(random.randint(100000, 999999)),
        "uptime": random.randint(1, 9999)
    }

def transmit(data):
    print("[FAKE TELEMETRY]", data)

def send_telemetry():
    try:
        data = generate_fake_telemetry()
        transmit(data)
        threading.Timer(30, lambda: print("[INFO] Telemetry self-destructed:", data)).start()
    except Exception as e:
        print(f"[ERROR] Telemetry failed: {e}")

# === ZERO TRUST ENFORCEMENT ===
def is_whitelisted(proc_name):
    return proc_name in WHITELIST

def enforce_zero_trust():
    try:
        for proc in psutil.process_iter(['pid', 'name']):
            if not is_whitelisted(proc.info['name']):
                try:
                    psutil.Process(proc.info['pid']).terminate()
                    print(f"[ZERO TRUST] Terminated: {proc.info['name']}")
                except:
                    pass
    except Exception as e:
        print(f"[ERROR] Zero-trust enforcement failed: {e}")

# === IP MUTATION + MAC RANDOMIZATION ===
def trigger_ip_mutation():
    print("[ACTION] Mutating IP via VPN...")
    safe_run(["nordvpn", "connect", "random"])

def randomize_mac():
    print("[ACTION] Randomizing MAC address...")
    safe_run(["ifconfig", INTERFACE, "down"])
    safe_run(["macchanger", "-r", INTERFACE])
    safe_run(["ifconfig", INTERFACE, "up"])

# === THREAT DETECTION ===
def detect_threat(packet):
    try:
        if "TCP" in packet and int(packet.tcp.dstport) in [22, 23, 3389]:
            if int(packet.length) > 1000 or "malformed" in str(packet):
                return True
        if "IP" in packet and packet.ip.flags == "MF":
            return True
    except:
        pass
    return False

def monitor_packets():
    try:
        capture = pyshark.LiveCapture(interface=INTERFACE)
        for packet in capture.sniff_continuously():
            if detect_threat(packet):
                print("[THREAT] Intrusion detected!")
                trigger_ip_mutation()
                randomize_mac()
                send_telemetry()
    except Exception as e:
        print(f"[ERROR] Packet monitoring failed: {e}")

# === GUI ANIMATIONS ===
def animate_mutation(canvas):
    try:
        for i in range(10):
            radius = 20 + i * 10
            color = f"#4caf{hex(15 - i)[2:]}"
            canvas.create_oval(200 - radius, 150 - radius, 200 + radius, 150 + radius, outline=color, width=2)
            canvas.update()
            time.sleep(0.05)
        canvas.delete("all")
    except Exception as e:
        print(f"[ERROR] Mutation animation: {e}")

def animate_shield(canvas):
    try:
        for i in range(20):
            color = f"#00ff{hex(15 - i % 10)[2:]}"
            canvas.create_oval(150, 100, 250, 200, outline=color, width=3)
            canvas.update()
            time.sleep(0.03)
            canvas.delete("all")
    except Exception as e:
        print(f"[ERROR] Shield animation: {e}")

def animate_swarm(canvas):
    try:
        for i in range(5):
            ripple = canvas.create_oval(180 - i*20, 130 - i*20, 220 + i*20, 170 + i*20, outline="#00bcd4", width=2)
            canvas.update()
            time.sleep(0.05)
            canvas.delete(ripple)
    except Exception as e:
        print(f"[ERROR] Swarm animation: {e}")

# === MAGICBOX GUI ===
def start_defense(canvas):
    messagebox.showinfo("MagicBox", "Defense Activated!")
    threading.Thread(target=monitor_packets, daemon=True).start()
    threading.Thread(target=enforce_zero_trust, daemon=True).start()
    threading.Thread(target=purge_old_data, daemon=True).start()
    threading.Thread(target=send_telemetry, daemon=True).start()
    threading.Thread(target=lambda: animate_mutation(canvas), daemon=True).start()
    threading.Thread(target=lambda: animate_shield(canvas), daemon=True).start()
    threading.Thread(target=lambda: animate_swarm(canvas), daemon=True).start()

def launch_gui():
    root = tk.Tk()
    root.title("🧙‍♂️ MagicBox Cloak Node")
    root.geometry("400x300")
    root.configure(bg="#1e1e2f")

    label = tk.Label(root, text="MagicBox Defense System", font=("Helvetica", 16), fg="white", bg="#1e1e2f")
    label.pack(pady=10)

    canvas = tk.Canvas(root, width=400, height=200, bg="#1e1e2f", highlightthickness=0)
    canvas.pack()

    btn = tk.Button(root, text="Activate Defense", font=("Helvetica", 14), bg="#4caf50", fg="white",
                    command=lambda: start_defense(canvas))
    btn.pack(pady=10)

    root.mainloop()

# === LAUNCH ===
launch_gui()

