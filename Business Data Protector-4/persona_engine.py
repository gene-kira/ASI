# persona_engine.py

import psutil
from utils import log_codex

def inject_persona(memory):
    active_ips = set()
    for conn in psutil.net_connections(kind='inet'):
        if conn.raddr:
            active_ips.add(conn.raddr.ip)

    for ip in active_ips:
        if ip in memory.get("blocked", []):
            log_codex(f"🧬 Persona injected for {ip}: Spectre")
            return "Spectre"
        elif ip.startswith("192.168."):
            log_codex(f"🧬 Persona injected for {ip}: Echo")
            return "Echo"

    log_codex("🧬 Persona injected: Oracle (default)")
    return "Oracle"

