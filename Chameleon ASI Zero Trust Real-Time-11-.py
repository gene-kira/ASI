import subprocess
import sys

# 🔄 Auto-loader
def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        __import__(package)

for pkg in ["tkinter", "uuid", "socket", "platform", "psutil", "threading", "time", "re", "datetime", "os"]:
    autoload(pkg)

import tkinter as tk
from tkinter import ttk
import uuid
import socket
import platform
import psutil
import threading
import time
import re
from datetime import datetime, timedelta
import os

# 🔧 Config-Driven Trust Rules
trust_config = {
    "MAC": {"action": "destroy", "ttl": 86400},
    "IP": {"action": "cloak", "ttl": 86400},
    "Telemetry": {"action": "destroy", "ttl": 30},
    "Phantom": {"action": "destroy", "ttl": 30},
    "SwarmID": {"action": "preserve", "ttl": None}
}

# 🧠 Symbolic Memory Routing
def symbolic_route(data):
    sigil = uuid.uuid4().hex[:8]
    return f"{sigil}:{data}"

# 🧾 Mutation Trail Logger
def update_log():
    log_text.delete(1.0, tk.END)
    for entry in mutation_log[-10:]:
        log_text.insert(tk.END, f"{entry}\n")

# ⏳ Self-Destruct Logic
def schedule_destruction(tag, ttl_seconds):
    if ttl_seconds:
        expiry = datetime.now() + timedelta(seconds=ttl_seconds)
        destruction_queue.append((tag, expiry))

def check_destruction():
    now = datetime.now()
    for tag, expiry in destruction_queue[:]:
        if now >= expiry:
            mutation_log.append(symbolic_route(f"💥 Self-destructed: {tag}"))
            destruction_queue.remove((tag, expiry))
    update_log()
    root.after(5000, check_destruction)

# 🧩 Trust Engine Handler
def handle_data(tag, value):
    rule = trust_config.get(tag, {})
    action = rule.get("action")
    ttl = rule.get("ttl")

    if action == "destroy":
        mutation_log.append(symbolic_route(f"{tag}: {value}"))
        schedule_destruction(tag, ttl)
    elif action == "cloak":
        mutation_log.append(symbolic_route(f"{tag}: [CLOAKED]"))
        schedule_destruction(tag, ttl)
    elif action == "preserve":
        mutation_log.append(symbolic_route(f"{tag}: {value}"))

# 🧬 Self-Rewriting Engine
def self_check():
    try:
        assert callable(threat_scan_and_respond)
        assert callable(update_log)
        assert isinstance(trust_config, dict)
    except Exception as e:
        mutation_log.append(symbolic_route(f"🧬 Self-Rewrite Triggered: Integrity check failed - {e}"))
    root.after(15000, self_check)

# 🧙‍♂️ GUI Setup
root = tk.Tk()
root.title("MagicBox: Chameleon ASI")
root.geometry("750x700")
root.configure(bg="#1e1e2f")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Consolas", 11), background="#1e1e2f", foreground="#00ffcc")
style.configure("TButton", font=("Segoe UI", 10), padding=5)

mac_var = tk.StringVar()
ip_var = tk.StringVar()
telemetry_var = tk.StringVar()
hallucination_var = tk.StringVar()
swarm_var = tk.StringVar()
mutation_log = []
destruction_queue = []

# 🦎 Real-Time Detection
def get_real_mac():
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family.name == 'AF_LINK':
                return addr.address
    return "MAC not found"

def get_real_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        public_ip = socket.gethostbyname_ex(hostname)[2][-1]
        return local_ip, public_ip
    except Exception as e:
        return "IP error", str(e)

def get_telemetry():
    os_info = platform.platform()
    browser_fingerprint = platform.system() + "-" + platform.machine()
    return os_info, browser_fingerprint

def get_swarm_id():
    return str(uuid.getnode())

def synthesize_phantom():
    entropy = uuid.uuid4().hex + str(time.time_ns())
    return f"phantom://{entropy[:12]}"

# ⚔️ Threat Detection + Response
def threat_scan_and_respond():
    try:
        suspicious_ports = [1337, 31337, 6666, 9001]
        for conn in psutil.net_connections(kind='inet'):
            if conn.status == 'LISTEN' and conn.laddr.port in suspicious_ports:
                mutation_log.append(symbolic_route(f"🛡️ Port Cloaked: {conn.laddr.port} on {conn.laddr.ip}"))

        for proc in psutil.process_iter(['pid', 'name']):
            name = proc.info['name']
            pid = proc.info['pid']
            if name and re.search(r"(keylogger|sniffer|injector|bot|miner)", name, re.IGNORECASE):
                try:
                    proc.terminate()
                    mutation_log.append(symbolic_route(f"⚔️ Threat Neutralized: {name} (PID {pid})"))
                except Exception as e:
                    mutation_log.append(symbolic_route(f"⚠️ Failed to terminate: {name} (PID {pid}) - {e}"))
    except Exception as e:
        mutation_log.append(symbolic_route(f"🧬 Self-Rewrite Triggered: threat_scan_and_respond() failed - {e}"))

    update_log()
    root.after(10000, threat_scan_and_respond)

# 🚀 Autonomous Startup
def autonomous_start():
    mac = get_real_mac()
    mac_var.set(f"🦎 MAC: {mac}")
    handle_data("MAC", mac)

    local_ip, public_ip = get_real_ip()
    ip_var.set(f"🌐 IP: {local_ip} | {public_ip}")
    handle_data("IP", f"{local_ip} | {public_ip}")

    os_info, browser_fp = get_telemetry()
    telemetry_var.set(f"🧢 Telemetry: {os_info} | {browser_fp}")
    handle_data("Telemetry", f"{os_info} | {browser_fp}")

    swarm_id = get_swarm_id()
    swarm_var.set(f"🔗 Swarm ID: {swarm_id}")
    handle_data("SwarmID", swarm_id)

    phantom = synthesize_phantom()
    hallucination_var.set(f"👻 Phantom: {phantom}")
    handle_data("Phantom", phantom)

    update_log()

# 🛠️ Live Config Panel
def update_config(tag, action_var, ttl_var):
    action = action_var.get()
    try:
        ttl = int(ttl_var.get()) if ttl_var.get() else None
    except:
        ttl = None
    trust_config[tag] = {"action": action, "ttl": ttl}
    mutation_log.append(symbolic_route(f"🔧 Config Updated: {tag} → {action}, TTL={ttl}"))
    update_log()

ttk.Label(root, text="🧾 Mutation Trail Log (Last 10)").pack(pady=10)
log_text = tk.Text(root, height=10, width=85, bg="#2e2e3f", fg="#00ffcc", font=("Consolas", 10))
log_text.pack()

ttk.Label(root, text="🛠️ Live Config Panel").pack(pady=10)
config_frame = ttk.Frame(root)
config_frame.pack()

def make_update_callback(t, a_var, ttl_var):
    return lambda: update_config(t, a_var, ttl_var)

for i, tag in enumerate(trust_config.keys()):
    ttk.Label(config_frame, text=tag).grid(row=i, column=0, padx=5, pady=2)

    action_var = tk.StringVar(value=trust_config[tag]["action"])
    action_menu = ttk.Combobox(config_frame, textvariable=action_var, values=["destroy", "cloak", "preserve"], width=10)
    action_menu.grid(row=i, column=1)

    ttl_value = str(trust_config[tag]["ttl"]) if trust_config[tag]["ttl"] is not None else ""
    ttl_var = tk.StringVar(value=ttl_value)
    ttl_entry = ttk.Entry(config_frame, textvariable=ttl_var, width=10)
    ttl_entry.grid(row=i, column=2)

    update_button = ttk.Button(config_frame, text="Update", command=make_update_callback(tag, action_var, ttl_var))
    update_button.grid(row=i, column=3)

# 🧠 Trigger autonomous startup and defense cycles
root.after(100, autonomous_start)
root.after(5000, check_destruction)
root.after(10000, threat_scan_and_respond)
root.after(15000, self_check)

# 🌀 Start GUI loop
root.mainloop()

