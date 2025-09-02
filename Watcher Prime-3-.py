# MagicBox Daemon - Mythic Edition
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
        from datetime import datetime
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "requests"])
        import tkinter, requests, socket, hashlib, uuid, threading
        from datetime import datetime

autoload()

import tkinter as tk
from tkinter import ttk
import requests, socket, hashlib, uuid, threading
from datetime import datetime

# 🧠 Codex Vault
codex_vault = []

# 🧾 GUI Setup
root = tk.Tk()
root.title("MagicBox Daemon")
root.geometry("900x700")
root.configure(bg="#1c1c2e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TButton", font=("Arial", 14), padding=10)
style.configure("TLabel", font=("Arial", 12), background="#1c1c2e", foreground="white")

# 📜 Codex Vault Viewer
codex_frame = tk.Frame(root, bg="#1c1c2e")
codex_frame.pack(fill="both", expand=True)

codex_list = tk.Listbox(codex_frame, font=("Courier", 10), bg="#2e2e3e", fg="white", selectbackground="#444")
codex_list.pack(fill="both", expand=True, padx=10, pady=10)

def update_codex_display():
    codex_list.delete(0, tk.END)
    for entry in codex_vault[-50:]:
        codex_list.insert(tk.END, f"{entry['timestamp']} | {entry['source']} | {entry['status']}")

# 🧾 Log Output
log_frame = tk.Frame(root, bg="#1c1c2e")
log_frame.pack(fill="x")

log_label = tk.Label(log_frame, text="System Log:", font=("Arial", 12), bg="#1c1c2e", fg="white")
log_label.pack(anchor="w", padx=10)

log_text = tk.Text(log_frame, height=6, bg="#2e2e3e", fg="white", font=("Courier", 10))
log_text.pack(fill="x", padx=10, pady=5)

def log_output(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

# 🧨 Self-Destruct Logic
def self_destruct(data_id, delay_sec):
    def destroy():
        for entry in codex_vault:
            if entry["id"] == data_id:
                entry["status"] = "destroyed"
        update_codex_display()
        log_output(f"💥 Data {data_id[:6]} self-destructed after {delay_sec}s")
    threading.Timer(delay_sec, destroy).start()

# 🛡️ Threat Monitor
def monitor_data(data_packet):
    if data_packet["channel"] == "backdoor":
        self_destruct(data_packet["id"], 3)
    elif data_packet.get("mac") or data_packet.get("ip"):
        self_destruct(data_packet["id"], 30)
    elif data_packet["type"] == "personal":
        self_destruct(data_packet["id"], 86400)
    elif data_packet["type"] == "fake_telemetry":
        self_destruct(data_packet["id"], 30)

# 🔁 Swarm Sync Pulse
def sync_pulse(source, hash_digest):
    log_output(f"🔁 Sync pulse from {source} | hash: {hash_digest[:10]}")

# 🧬 Replicator Logic
def spawn_clone(trait):
    clone_id = f"Clone_{trait}_{uuid.uuid4().hex[:6]}"
    codex_vault.append({
        "id": clone_id,
        "source": "Replicator",
        "timestamp": datetime.utcnow().isoformat(),
        "hash": trait,
        "status": "active"
    })
    update_codex_display()
    log_output(f"🧬 Spawned {clone_id} with trait: {trait}")

# 🧪 Port Scanner
def scan_ports():
    open_ports = []
    for port in range(1, 1025):  # Scanning common ports
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.settimeout(0.01)
                result = s.connect_ex(('localhost', port))
                if result == 0:
                    open_ports.append(port)
        except:
            pass
    return open_ports

# 🧿 Ingest Logic
def ingest_from_ports():
    ports = scan_ports()
    for port in ports:
        try:
            url = f"http://localhost:{port}/telemetry"
            response = requests.get(url, timeout=1)
            response.raise_for_status()
            data = response.text
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
            codex_vault.append(data_packet)
            update_codex_display()
            sync_pulse(data_packet["source"], hash_digest)
            monitor_data(data_packet)
            log_output(f"🧿 Ingested from Port {port}")
        except:
            pass

# 🔘 GUI Buttons
def start_ingest():
    log_output("🚀 Starting telemetry ingest...")
    threading.Thread(target=ingest_from_ports).start()

def spawn_stealth():
    spawn_clone("stealth")

def spawn_fallback():
    spawn_clone("fallback")

def spawn_hunter():
    spawn_clone("anomaly_hunter")

btn_frame = tk.Frame(root, bg="#1c1c2e")
btn_frame.pack(pady=10)

ttk.Button(btn_frame, text="Start Ingest", command=start_ingest).grid(row=0, column=0, padx=10)
ttk.Button(btn_frame, text="Spawn Stealth Clone", command=spawn_stealth).grid(row=0, column=1, padx=10)
ttk.Button(btn_frame, text="Spawn Fallback Clone", command=spawn_fallback).grid(row=0, column=2, padx=10)
ttk.Button(btn_frame, text="Spawn Hunter Clone", command=spawn_hunter).grid(row=0, column=3, padx=10)

# 🧙 Launch GUI
log_output("🧿 MagicBox Daemon Ready")
root.mainloop()

