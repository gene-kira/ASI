# main.py

import threading, uuid, platform, time
from vault import monitor_data, ingest_data
from config import TIMERS, PERSONAL_DATA_KEYS, TELEMETRY_FAKE
from swarm import track_ip_connections, swarm_sync_decision
from gui import launch_gui

def auto_ingest():
    while True:
        ingest_data("MAC_address", uuid.getnode(), TIMERS["mac_ip_fast"])
        ingest_data("IP_address", platform.node(), TIMERS["mac_ip_fast"])
        for key in PERSONAL_DATA_KEYS:
            ingest_data(key, f"simulated_{key}", TIMERS["personal_data"])
        for key, value in TELEMETRY_FAKE.items():
            ingest_data(f"telemetry_{key}", value, TIMERS["telemetry_fake"], source="external")
        ingest_data("backdoor_leak", "unauthorized_packet", TIMERS["backdoor_leak"], source="external")
        swarm_sync_decision()
        time.sleep(10)

def launch_system():
    threading.Thread(target=monitor_data, daemon=True).start()
    threading.Thread(target=auto_ingest, daemon=True).start()
    threading.Thread(target=track_ip_connections, daemon=True).start()
    launch_gui()

if __name__ == "__main__":
    launch_system()

