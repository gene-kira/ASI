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

geo = IPGeoLocator(token=GEO_TOKEN)
gui = TacticalGUI()
ingest = RealTimeIngest()
codex = SymbolicCodex()
swarm = SwarmNode(node_id="KS-01")
sanitizer = DataSanitizer()

active_personas = ["decoy_alpha", "observer_beta"]
threat_history = []

def rotate_persona():
    if len(active_personas) > 3:
        active_personas.pop(0)
    active_personas.append(f"phantom_{int(time.time()) % 100}")
    gui.update_personas(active_personas)
    mutation = codex.mutate("persona", "System", f"Rotated to {active_personas[-1]}")
    gui.update_codex(mutation)

def ingest_loop():
    ingest.activate_live_stream()
    while True:
        packet = ingest.get_live_state()
        src_ip = packet["src_ip"]
        dst_ip = packet["dst_ip"]

        src_info = geo.lookup(src_ip)
        dst_info = geo.lookup(dst_ip)

        gui.update_ip_log(src_info)
        gui.update_ip_log(dst_info)

        ancestry = {
            "timestamp": packet["timestamp"],
            "src": src_ip,
            "dst": dst_ip,
            "protocol": packet["protocol"],
            "payload_size": len(packet["payload"])
        }
        threat_history.append(ancestry)
        gui.update_threats(f"{src_ip} → {dst_ip} | {packet['protocol']} | {len(packet['payload'])} bytes")

        vote = swarm.vote_threat(packet_id=str(time.time()), ancestry=ancestry)
        swarm.sync_vote(vote)

        if vote["severity"] == "high":
            rotate_persona()

        mutation = codex.mutate("threat", src_ip, f"Protocol {packet['protocol']} → {dst_ip}")
        gui.update_codex(mutation)

        sanitizer.tag_mac_ip(src_ip)
        sanitizer.tag_mac_ip(dst_ip)
        sanitizer.tag_fake_telemetry({"cpu": 99.9, "temp": 999})
        sanitizer.purge_expired()

        time.sleep(0.5)

threading.Thread(target=ingest_loop, daemon=True).start()
gui.launch_interface()

