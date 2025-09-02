# Autonomous MagicBox Daemon with Rewrite Logic
import subprocess, sys

# 🧙 Autoloader
def autoload():
    try:
        import tkinter
        import requests
        import socket
        import hashlib
        import uuid
        import threading
        import random
        import json
        import os
        from datetime import datetime
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import tkinter, requests, socket, hashlib, uuid, threading, random, json, os
        from datetime import datetime

autoload()

import tkinter as tk
from tkinter import ttk
import requests, socket, hashlib, uuid, threading, random, json, os
from datetime import datetime

# 🔗 Rewrite Logic (inline from rewrite.py)
CODEX_FILE = "fusion_codex.json"

def detect_density_spike(flows):
    if len(flows) < 10:
        return False
    recent = flows[-10:]
    avg_entropy = sum(p.entropy for p in recent) / len(recent)
    variance = max(p.entropy for p in recent) - min(p.entropy for p in recent)
    return variance > 2.5 and avg_entropy > 7.0

def initiate_mutation_vote(pulse):
    votes = [random.choice(["yes", "no"]) for _ in range(5)]
    return votes.count("yes") >= 3

def rewrite_optimization_logic():
    new_threshold = random.randint(6, 8)
    logic = f"entropy > {new_threshold}"
    timestamp = datetime.utcnow().isoformat()
    print(f"[🧠 Rewrite] New cloaking threshold: {logic}")
    return {
        "logic": logic,
        "timestamp": timestamp,
        "trigger": "symbolic_density_spike",
        "consensus": "mutation_vote_passed"
    }

def store_rewrite_codex(entry):
    codex = []
    if os.path.exists(CODEX_FILE):
        with open(CODEX_FILE, "r") as f:
            codex = json.load(f)
    codex.append(entry)
    with open(CODEX_FILE, "w") as f:
        json.dump(codex, f, indent=2)

# 🧠 Codex Vault
codex_vault = []
flows = []

class Packet:
    def __init__(self, data):
        self.data = data
        self.entropy = self.calculate_entropy()

    def calculate_entropy(self):
        from collections import Counter
        counts = Counter(self.data)
        total = len(self.data)
        return -sum((count / total) * (count / total).bit_length() for count in counts.values())

# 🧾 GUI Setup
root = tk.Tk()
root.title("MagicBox Daemon")
root.geometry("900x700")
root.configure(bg="#1c1c2e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 12), background="#1c1c2e", foreground="white")

codex_frame = tk.Frame(root, bg="#1c1c2e")
codex_frame.pack(fill="both", expand=True)

codex_list = tk.Listbox(codex_frame, font=("Courier", 10), bg="#2e2e3e", fg="white", selectbackground="#444")
codex_list.pack(fill="both", expand=True, padx=10, pady=10)

def update_codex_display():
    codex_list.delete(0, tk.END)
    for entry in codex_vault[-50:]:
        codex_list.insert(tk.END, f"{entry['timestamp']} | {entry['source']} | {entry['status']}")

log_frame = tk.Frame(root, bg="#1c1c2e")
log_frame.pack(fill="x")

log_label = tk.Label(log_frame, text="System Log:", font=("Arial", 12), bg="#1c1c2e", fg="white")
log_label.pack(anchor="w", padx=10)

log_text = tk.Text(log_frame, height=6, bg="#2e2e3e", fg="white", font=("Courier", 10))
log_text.pack(fill="x", padx=10, pady=5)

def log_output(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

def self_destruct(data_id, delay_sec):
    def destroy():
        for entry in codex_vault:
            if entry["id"] == data_id:
                entry["status"] = "destroyed"
        update_codex_display()
        log_output(f"💥 Data {data_id[:6]} self-destructed after {delay_sec}s")
    threading.Timer(delay_sec, destroy).start()

def monitor_data(data_packet):
    if data_packet["channel"] == "backdoor":
        self_destruct(data_packet["id"], 3)
    elif data_packet.get("mac") or data_packet.get("ip"):
        self_destruct(data_packet["id"], 30)
    elif data_packet["type"] == "personal":
        self_destruct(data_packet["id"], 86400)
    elif data_packet["type"] == "fake_telemetry":
        self_destruct(data_packet["id"], 30)

def sync_pulse(source, hash_digest):
    log_output(f"🔁 Sync pulse from {source} | hash: {hash_digest[:10]}")

def spawn_clone():
    traits = random.sample(["stealth", "fallback", "anomaly_hunter"], k=2)
    clone_id = f"Clone_{uuid.uuid4().hex[:6]}"
    codex_vault.append({
        "id": clone_id,
        "source": "Replicator",
        "timestamp": datetime.utcnow().isoformat(),
        "hash": "|".join(traits),
        "status": "active"
    })
    update_codex_display()
    sync_pulse(clone_id, hashlib.sha256(clone_id.encode()).hexdigest())
    log_output(f"🧬 Spawned {clone_id} with traits: {', '.join(traits)}")

def scan_ports():
    open_ports = []
    for port in range(1, 1025):
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.01)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    open_ports.append(port)
        except:
            pass
    return open_ports

def ingest_from_ports():
    ports = scan_ports()
    for port in ports:
        try:
            url = f"http://localhost:{port}/telemetry"
            response = requests.get(url, timeout=1)
            response.raise_for_status()
            data = response.text
            packet = Packet(data)
            flows.append(packet)
            hash_digest = hashlib.sha256(data.encode()).hexdigest()
            data_packet = {
                "id": str(uuid.uuid4()),
                "source": f"Port {port}",
                "timestamp": datetime.utcnow().isoformat(),
                "hash": hash_digest,
                "status": "active",
                "channel": "normal",
                "type": "real"
            }
            if any(k in data.lower() for k in ["face", "fingerprint", "ssn", "license", "address", "phone"]):
                data_packet["type"] = "personal"
            codex_vault.append(data_packet)
            update_codex_display()
            sync_pulse(data_packet["source"], hash_digest)
            monitor_data(data_packet)
            log_output(f"🧿 Ingested from Port {port}")

            # 🔥 Rewrite Trigger
            if detect_density_spike(flows):
                log_output("⚠️ Symbolic density spike detected")
                if initiate_mutation_vote(packet):
                    rewrite = rewrite_optimization_logic()
                    store_rewrite_codex(rewrite)
                    codex_vault.append({
                        "id": str(uuid.uuid4()),
                        "source": "RewriteEngine",
                        "timestamp": rewrite["timestamp"],
                        "hash": rewrite["logic"],
                        "status": "active"
                    })
                    update_codex_display()
                    log_output(f"🧠 Optimization logic rewritten: {rewrite['logic']}")

        except:
            pass

def loop_ingest():
    ingest_from_ports()
    threading.Timer(10, loop_ingest).start()

def loop_replicate():
    spawn_clone()
    threading.Timer(30, loop_replicate).start()

log_output("🧿 MagicBox Daemon Activated with Rewrite Engine")
loop_ingest()
loop_replicate()
root.mainloop()

