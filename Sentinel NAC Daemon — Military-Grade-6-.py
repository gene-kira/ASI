import socket
import threading
import time
import random
from datetime import datetime
import tkinter as tk
from tkinter import ttk
import signal
import psutil

# 🛡️ Interrupt Shield
def block_interrupt(signum, frame):
    print("\n🛡️ Interrupt blocked. EchoNull shell remains active.")

signal.signal(signal.SIGINT, block_interrupt)
signal.signal(signal.SIGTERM, block_interrupt)

# 🧠 Global State
NODE_ID = "sovereign-node-001"
TRUST_SCORE_THRESHOLD = 70
QUARANTINE_LOG = []
SWARM_NODES = ["node_alpha", "node_beta", "node_gamma"]
MUTATION_HISTORY = []
LINEAGE_LOG = []
DRIFT_MAP = {}
LAST_PURGE = "None"
LAST_MUTATION = "None"

# 🔐 Zero-Trust AI/ASI Firewall
def validate_entity(entity):
    if entity in ["AI", "ASI", "unknown"]:
        narrate("Zero-Trust Trigger", f"Entity {entity} blocked")
        push_alert(f"Blocked untrusted entity: {entity}")
        return False
    return True

# 🔥 Backdoor Detection + 3s Self-Destruct
def eject_backdoor_payload(data):
    narrate("Backdoor Detected", "Payload flagged for destruction")
    push_alert("Backdoor payload detected and scheduled for purge")
    threading.Timer(3.0, lambda: destroy_data(data)).start()

# ⏳ MAC/IP Auto-Purge After 30s
def register_network_identity(mac, ip):
    identity = {"mac": mac, "ip": ip}
    narrate("Network Identity", f"Registered MAC/IP: {mac}/{ip}")
    threading.Timer(30.0, lambda: destroy_data(identity)).start()

# 🧬 Bio-Data Expiry Enforcement (1 Day)
def store_personal_data(data):
    narrate("Bio-Data Stored", "Personal data accepted under 1-day policy")
    threading.Timer(86400.0, lambda: destroy_data(data)).start()

# 🛰️ Fake Telemetry + 30s Cloak Purge
def transmit_fake_telemetry():
    fake_data = {"cpu": random.randint(1, 10), "mem": random.randint(1, 10)}
    narrate("Telemetry Cloak", f"Fake data transmitted: {fake_data}")
    threading.Timer(30.0, lambda: destroy_data(fake_data)).start()

# 💣 Data Purge Logic
def destroy_data(data):
    del data
    narrate("Self-Destruct", "Sensitive data purged")

# 🧠 Symbolic Feedback
def narrate(event, details):
    timestamp = datetime.utcnow().isoformat()
    log = f"[{timestamp}] {event}: {details}"
    MUTATION_HISTORY.append(log)
    update_gui()
    print(log)

# 🧬 Lineage Broadcasting
def broadcast_lineage(event, detail):
    entry = f"[{datetime.utcnow().isoformat()}] {event}: {detail}"
    LINEAGE_LOG.append(entry)
    narrate("Lineage Broadcast", entry)

# 🛰️ Swarm Sync Overlay
def sync_with_swarm():
    payload = {
        "node": NODE_ID,
        "mutation": LAST_MUTATION,
        "purge": LAST_PURGE,
        "timestamp": datetime.utcnow().isoformat()
    }
    for peer in SWARM_NODES:
        narrate("Swarm Sync", f"Broadcasting to {peer}: {payload}")
        # Placeholder for real sync logic

# 🔄 Mutation Voting + Ritual Override
def cast_mutation_vote(reason):
    vote = random.choice(["approve", "deny"])
    narrate("Mutation Vote", f"Vote on {reason}: {vote}")
    return vote

def request_override(reason):
    votes = [cast_mutation_vote(reason) for _ in SWARM_NODES]
    if votes.count("approve") > len(votes) // 2:
        narrate("Override Consensus", f"Override approved for: {reason}")
        push_alert(f"Override triggered: {reason}")
        mutate_daemon()
    else:
        narrate("Override Denied", f"Consensus failed for: {reason}")
        push_alert(f"Override blocked: {reason}")

# 🧭 Quantum Drift Map
def update_drift_map(ip, entropy):
    DRIFT_MAP[ip] = {
        "entropy": entropy,
        "timestamp": datetime.utcnow().isoformat()
    }
    narrate("Quantum Drift", f"Entropy {entropy} detected from {ip}")
    push_alert(f"Quantum drift anomaly from {ip}")

# 🧬 Mutation Logic
def mutate_daemon():
    global LAST_MUTATION
    mutation_id = f"mut_{random.randint(1000,9999)}"
    LAST_MUTATION = mutation_id
    narrate("Mutation", f"Daemon evolved into {mutation_id}")
    broadcast_lineage("Mutation", mutation_id)
    sync_with_swarm()

# 🔥 Autonomous Purge Logic
def purge_node(ip):
    global LAST_PURGE
    QUARANTINE_LOG.append(ip)
    LAST_PURGE = ip
    narrate("Purge", f"Node {ip} quarantined due to drift anomaly")
    broadcast_lineage("Purge", ip)
    sync_with_swarm()
    push_alert(f"Node {ip} purged due to anomaly")

# 🧠 Packet Inspection
def inspect_packet(packet, ip):
    trust_score = sum(packet) % 100
    entropy = sum(byte % 7 for byte in packet) % 100
    update_drift_map(ip, entropy)
    if trust_score < TRUST_SCORE_THRESHOLD or entropy > 80:
        purge_node(ip)
    else:
        narrate("Access Granted", f"Node {ip} passed trust score {trust_score}")

# 🧵 Listener Thread
def start_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(("0.0.0.0", 9999))
    narrate("Daemon Start", "Listening on port 9999")
    while True:
        data, addr = sock.recvfrom(1024)
        inspect_packet(list(data), addr[0])

# 🔍 Port Monitor
def monitor_ports():
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
        status = conn.status
        pid = conn.pid
        narrate("Port Scan", f"Local: {laddr} | Remote: {raddr} | Status: {status} | PID: {pid}")
        if conn.raddr and conn.raddr.ip not in ["127.0.0.1", "0.0.0.0"]:
            if conn.status not in ["ESTABLISHED", "LISTEN"]:
                purge_node(conn.raddr.ip)

def start_port_monitor():
    narrate("Port Monitor", "Scanning all ports every 10 seconds")
    while True:
        monitor_ports()
        time.sleep(10)

# 🎨 MagicBox GUI — Executive Dashboard
root = tk.Tk()
root.title("🧙‍♂️ Sentinel Sovereign — MagicBox Edition")
root.geometry("850x700")
root.configure(bg="#1a1a1a")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", foreground="#1a1a1a", background="#00ff00", font=("Courier", 12, "bold"))
style.configure("TLabel", foreground="#00ff00", background="#1a1a1a", font=("Courier", 10))
style.configure("TFrame", background="#1a1a1a")

frame = ttk.Frame(root)
frame.pack(padx=20, pady=20, fill="both", expand=True)

status_label = ttk.Label(frame, text="✅ Daemon Active", font=("Courier", 14, "bold"))
status_label.pack(pady=10)

mutation_label = ttk.Label(frame, text="Last Mutation: None")
mutation_label.pack()

purge_label = ttk.Label(frame, text="Last Purge: None")
purge_label.pack()

swarm_label = ttk.Label(frame, text=f"Swarm Nodes: {', '.join(SWARM_NODES)}")
swarm_label.pack(pady=10)

log_box = tk.Text(frame, height=15, bg="#000", fg="#0f0", font=("Courier", 9))
log_box.pack(fill="both", expand=True)

alert_box = tk.Text(frame, height=5, bg="#111", fg="#ff0000", font=("Courier", 10))
alert_box.pack(fill="x", pady=5)

drift_box = tk.Text(frame, height=8, bg="#111", fg="#00ffff", font=("Courier", 9))
drift_box.pack(fill="x", pady=5)

def update_gui():
    mutation_label.config(text=f"Last Mutation: {LAST_MUTATION}")
    purge_label.config(text=f"Last Purge: {LAST_PURGE}")
    log_box.delete(1.0, tk.END)
    for log in MUTATION_HISTORY[-10:]:
        log_box.insert(tk.END, log + "\n")
    update_drift_gui()

def update_drift_gui():
    drift_box.delete(1.0, tk.END)
    for ip, data in DRIFT_MAP.items():
        drift_box.insert(tk.END, f"{ip} → Entropy: {data['entropy']} @ {data['timestamp']}\n")

def push_alert(message):
    alert_box.insert(tk.END, f"[ALERT] {message}\n")
    alert_box.see(tk.END)

def trigger_mutation():
    mutate_daemon()

def trigger_override():
    request_override("Manual escalation")

# 🧙 Ritual Override Button
override_button = ttk.Button(frame, text="Request Ritual Override", command=trigger_override)
override_button.pack(pady=10)

# 🚀 Launch Sequence
threading.Thread(target=start_listener, daemon=True).start()
threading.Thread(target=start_port_monitor, daemon=True).start()
transmit_fake_telemetry()
update_gui()
root.mainloop()


