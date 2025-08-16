import threading
from modules.packet_sniffer import PacketSniffer
from modules.geoip_mapper import GeoIPMapper
from modules.vault_engine import VaultEngine
from modules.reasoning import ReasoningEngine
from modules.swarm_dashboard import SwarmDashboard
from modules.gui_overlay import GUIOverlay

# 🔮 Mutation Hooks
class MutationHooks:
    def __init__(self, gui=None):
        self.gui = gui

    def log_mutation(self, msg):
        print(f"[Mutation] {msg}")
        if self.gui:
            self.gui.update_status(msg)

# 🧠 Initialize Core Modules
def initialize_modules():
    vault = VaultEngine(ttl=90)
    dashboard = SwarmDashboard()
    geoip = GeoIPMapper(mutation_hook=mutator)
    reasoning = ReasoningEngine(target_file="main.py", mutation_hook=mutator)
    sniffer = PacketSniffer(mutation_hook=mutator)
    return vault, dashboard, geoip, reasoning, sniffer

# 🌐 Background Threads
def start_sniffer(sniffer):
    sniffer.start_sniffing()

def start_reasoning(reasoning):
    while True:
        reasoning.scan_and_repair()
        time.sleep(30)

def start_dashboard_purge(dashboard):
    while True:
        dashboard.purge_stale()
        time.sleep(60)

# 🚀 Launch System
if __name__ == "__main__":
    import time

    gui = GUIOverlay(None)
    mutator = MutationHooks(gui)
    vault, dashboard, geoip, reasoning, sniffer = initialize_modules()
    gui.brain = mutator  # Link GUI to mutation brain

    # 🧵 Threads
    threading.Thread(target=start_sniffer, args=(sniffer,), daemon=True).start()
    threading.Thread(target=start_reasoning, args=(reasoning,), daemon=True).start()
    threading.Thread(target=start_dashboard_purge, args=(dashboard,), daemon=True).start()

    # 🔐 Vault Test
    vault.save("test", "Encrypted swarm seed")
    mutator.log_mutation(f"Vault test: {vault.retrieve('test')}")

    # 🌍 GeoIP Test
    location = geoip.map_ip("8.8.8.8")
    mutator.log_mutation(f"GeoIP test: 8.8.8.8 → {location}")

    # 🌀 Swarm Node Test
    dashboard.register_node("192.168.1.101")

    # 🎭 GUI Launch
    gui.run()

