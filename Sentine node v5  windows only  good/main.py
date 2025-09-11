# main.py — SentinelNode Runtime Core
import threading, time, ctypes, sys, os
from modules.ingest import RealTimeIngest
from modules.geo import IPGeoLocator
from modules.gui import TacticalGUI
from modules.codex import SymbolicCodex
from modules.swarm import SwarmNode
from modules.sanitizer import DataSanitizer

GEO_TOKEN = "YOUR_API_TOKEN"

def require_admin():
    if os.name == 'nt':
        try:
            is_admin = ctypes.windll.shell32.IsUserAnAdmin()
        except:
            is_admin = False
        if not is_admin:
            params = ' '.join([f'"{arg}"' for arg in sys.argv])
            ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, params, None, 1)
            sys.exit()

require_admin()

# Initialize modules
geo = IPGeoLocator(token=GEO_TOKEN)
gui = TacticalGUI()
ingest = RealTimeIngest()
codex = SymbolicCodex()
swarm = SwarmNode(node_id="KS-01")
sanitizer = DataSanitizer()

active_personas = ["decoy_alpha", "observer_beta"]
threat_history = []
last_hash = None

def rotate_persona():
    global last_hash
    if len(active_personas) > 3:
        active_personas.pop(0)
    new_persona = f"phantom_{int(time.time()) % 100}"
    active_personas.append(new_persona)
    gui.update_personas(active_personas)
    mutation, hash_val = codex.mutate("persona", "System", f"Rotated to {new_persona}", parent_hash=last_hash)
    gui.update_codex(mutation)
    gui.update_ancestry(f"[PERSONA] {mutation}")
    last_hash = hash_val

def ingest_loop():
    global last_hash
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
            "payload_size": len(packet["payload"]),
            "persona": active_personas[-1]
        }
        threat_history.append(ancestry)
        gui.update_threats(f"{src_ip} → {dst_ip} | {packet['protocol']} | {len(packet['payload'])} bytes")

        # Swarm voting
        vote = swarm.vote_threat(packet_id=str(time.time()), ancestry=ancestry)
        swarm.sync_vote(vote)
        gui.update_swarm(vote)

        # Lockdown trigger
        if vote["severity"] == "high":
            rotate_persona()
            if swarm.lockdown_triggered:
                mutation, hash_val = codex.mutate("lockdown", "Swarm", "Consensus triggered lockdown", ancestry, parent_hash=last_hash)
                gui.update_codex(mutation)
                gui.update_ancestry(f"[LOCKDOWN] {mutation}")
                gui.update_lockdown("🛡️ LOCKDOWN ACTIVE — Swarm consensus reached")
                last_hash = hash_val

        # Codex mutation
        mutation, hash_val = codex.mutate("threat", src_ip, f"Protocol {packet['protocol']} → {dst_ip}", ancestry, parent_hash=last_hash)
        gui.update_codex(mutation)
        gui.update_ancestry(f"[THREAT] {mutation}")
        last_hash = hash_val

        # Data hygiene
        sanitizer.tag_mac_ip(src_ip)
        sanitizer.tag_mac_ip(dst_ip)
        sanitizer.tag_fake_telemetry({"cpu": 99.9, "temp": 999})
        sanitizer.purge_expired()

        time.sleep(0.5)

# Launch GUI and ingest loop
threading.Thread(target=ingest_loop, daemon=True).start()
gui.launch_interface()

