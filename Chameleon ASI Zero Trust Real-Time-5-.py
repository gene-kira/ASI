# MagicBox: Chameleon ASI (Response Edition)
# Autonomous, real-time sentinel with threat detection, response engine, and symbolic mutation trails

import subprocess
import sys

# 🔄 Auto-loader
def autoload(package):
    try:
        __import__(package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        __import__(package)

for pkg in ["tkinter", "uuid", "socket", "platform", "psutil", "threading", "time", "re", "datetime"]:
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

# 🧠 Symbolic Memory Routing
def symbolic_route(data):
    sigil = uuid.uuid4().hex[:8]
    return f"{sigil}:{data}"

# 🦎 Real MAC Detection
def get_real_mac():
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family.name == 'AF_LINK':
                return addr.address
    return "MAC not found"

# 🌐 Real IP Detection
def get_real_ip():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        public_ip = socket.gethostbyname_ex(hostname)[2][-1]
        return local_ip, public_ip
    except Exception as e:
        return "IP error", str(e)

# 🧢 Real Telemetry
def get_telemetry():
    os_info = platform.platform()
    browser_fingerprint = platform.system() + "-" + platform.machine()
    return os_info, browser_fingerprint

# 🔗 Real Swarm Identity
def get_swarm_id():
    return str(uuid.getnode())

# 👻 Hallucination Synthesis
def synthesize_phantom():
    entropy = uuid.uuid4().hex + str(time.time_ns())
    phantom = f"phantom://{entropy[:12]}"
    return phantom

# 🧾 Mutation Trail Logger
def update_log():
    log_text.delete(1.0, tk.END)
    for entry in mutation_log[-10:]:
        log_text.insert(tk.END, f"{entry}\n")

# ⏳ Self-Destruct Logic
def schedule_destruction(tag, ttl_seconds):
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

# ⚔️ Threat Detection + Response Engine
def threat_scan_and_respond():
    suspicious_ports = [1337, 31337, 6666, 9001]
    flagged = []

    # Scan open ports
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN' and conn.laddr.port in suspicious_ports:
            flagged.append(f"Port {conn.laddr.port} open on {conn.laddr.ip}")
            mutation_log.append(symbolic_route(f"🛡️ Port Cloaked: {conn.laddr.port} on {conn.laddr.ip}"))

    # Scan and terminate suspicious processes
    for proc in psutil.process_iter(['pid', 'name']):
        name = proc.info['name']
        pid = proc.info['pid']
        if name and re.search(r"(keylogger|sniffer|injector|bot|miner)", name, re.IGNORECASE):
            try:
                proc.terminate()
                mutation_log.append(symbolic_route(f"⚔️ Threat Neutralized: {name} (PID {pid})"))
            except Exception as e:
                mutation_log.append(symbolic_route(f"⚠️ Failed to terminate: {name} (PID {pid}) - {e}"))

    update_log()
    root.after(10000, threat_scan_and_respond)

# 🚀 Autonomous Startup
def autonomous_start():
    mac = get_real_mac()
    mac_var.set(f"🦎 Real MAC: {mac}")
    mutation_log.append(symbolic_route(mac))
    schedule_destruction("MAC", 86400)

    local_ip, public_ip = get_real_ip()
    ip_var.set(f"🌐 Local IP: {local_ip} | Public IP: {public_ip}")
    mutation_log.append(symbolic_route(local_ip))
    mutation_log.append(symbolic_route(public_ip))
    schedule_destruction("IP", 86400)

    os_info, browser_fp = get_telemetry()
    telemetry_var.set(f"🧢 OS: {os_info} | Fingerprint: {browser_fp}")
    mutation_log.append(symbolic_route(os_info))
    mutation_log.append(symbolic_route(browser_fp))
    schedule_destruction("Telemetry", 30)

    swarm_id = get_swarm_id()
    swarm_var.set(f"🔗 Swarm ID: {swarm_id}")
    mutation_log.append(symbolic_route(swarm_id))
    schedule_destruction("SwarmID", 86400)

    phantom = synthesize_phantom()
    hallucination_var.set(f"👻 Phantom: {phantom}")
    mutation_log.append(symbolic_route(phantom))
    schedule_destruction("Phantom", 30)

    update_log()

# 🧙‍♂️ GUI Setup
root = tk.Tk()
root.title("MagicBox: Chameleon ASI")
root.geometry("650x500")
root.configure(bg="#1e1e2f")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Consolas", 11), background="#1e1e2f", foreground="#00ffcc")

mac_var = tk.StringVar()
ip_var = tk.StringVar()
telemetry_var = tk.StringVar()
hallucination_var = tk.StringVar()
swarm_var = tk.StringVar()
mutation_log = []
destruction_queue = []

ttk.Label(root, text="🧙 MagicBox: Chameleon ASI (Response Edition)").pack(pady=10)
ttk.Label(root, textvariable=mac_var).pack()
ttk.Label(root, textvariable=ip_var).pack()
ttk.Label(root, textvariable=telemetry_var).pack()
ttk.Label(root, textvariable=hallucination_var).pack()
ttk.Label(root, textvariable=swarm_var).pack()

ttk.Label(root, text="🧾 Mutation Trail Log (Last 10)").pack(pady=10)
log_text = tk.Text(root, height=10, width=75, bg="#2e2e3f", fg="#00ffcc", font=("Consolas", 10))
log_text.pack()

ttk.Label(root, text="🔄 Autonomous startup complete. Response Engine active.").pack(pady=10)

root.after(100, autonomous_start)
root.after(5000, check_destruction)
root.after(10000, threat_scan_and_respond)
root.mainloop()

# 🧠 Trigger autonomous startup and defense cycles
root.after(100, autonomous_start)               # Launch all modules
root.after(5000, check_destruction)             # Begin self-destruct checks
root.after(10000, threat_scan_and_respond)      # Begin threat detection + response loop

# 🌀 Start GUI loop
root.mainloop()

