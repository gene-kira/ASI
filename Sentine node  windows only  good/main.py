# main.py — SentinelNode Runtime Core
import threading
import time
import ctypes
import sys
import os

from modules.ingest import RealTimeIngest
from modules.geo import IPGeoLocator
from modules.gui import TacticalGUI

# 🔐 Replace with your IPinfo token
GEO_TOKEN = "YOUR_API_TOKEN"

# Elevate to admin if needed (Windows only)
def require_admin():
    if os.name == 'nt':
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False
        if not is_admin:
            print("[ELEVATE] Relaunching with admin privileges...")
            params = ' '.join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit()

require_admin()

# Initialize modules
geo = IPGeoLocator(token=GEO_TOKEN)
gui = TacticalGUI()
ingest = RealTimeIngest()

# Threat ancestry tracker
threat_history = []

# Active persona state
active_personas = ["decoy_alpha", "observer_beta"]

# Swarm sync stub
def sync_to_swarm(packet, ancestry):
    print(f"[SWARM] Syncing {packet['src_ip']} → {packet['dst_ip']} | Ancestry: {ancestry}")

def ingest_loop():
    ingest.activate_live_stream()
    while True:
        packet = ingest.get_live_state()
        src_ip = packet["src_ip"]
        dst_ip = packet["dst_ip"]

        # Geolocation
        src_info = geo.lookup(src_ip)
        dst_info = geo.lookup(dst_ip)

        gui.update_ip_log(src_info)
        gui.update_ip_log(dst_info)

        # Threat ancestry
        ancestry = {
            "timestamp": packet["timestamp"],
            "src": src_ip,
            "dst": dst_ip,
            "protocol": packet["protocol"],
            "payload_size": len(packet["payload"])
        }
        threat_history.append(ancestry)
        gui.update_threats(f"{src_ip} → {dst_ip} | {packet['protocol']} | {len(packet['payload'])} bytes")

        # Persona mutation
        if b"\x16\x03" in packet["payload"] and "mutant_gamma" not in active_personas:
            active_personas.append("mutant_gamma")
            gui.update_codex("[PERSONA] Mutant Gamma activated.")

        gui.update_personas(active_personas)

        # Swarm sync
        sync_to_swarm(packet, ancestry)

        # Codex feedback
        codex_msg = (
            f"[{time.strftime('%H:%M:%S')}] {src_ip} → {dst_ip} | "
            f"Protocol: {packet['protocol']} | Personas: {', '.join(active_personas)}"
        )
        gui.update_codex(codex_msg)

# Launch GUI and ingest loop
threading.Thread(target=ingest_loop, daemon=True).start()
gui.launch_interface()

