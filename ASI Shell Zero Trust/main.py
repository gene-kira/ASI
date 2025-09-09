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
        for k in PERSONAL_DATA_KEYS:
            ingest_data(k, f"simulated_{k}", TIMERS["personal_data"])
        for k, v in TELEMETRY_FAKE.items():
            ingest_data(f"telemetry_{k}", v, TIMERS["telemetry_fake"], source="external")
        ingest_data("backdoor_leak", "unauthorized_packet", TIMERS["backdoor_leak"], source="external")
        swarm_sync_decision()
        time.sleep(10)

# Launch Threads
threading.Thread(target=monitor_data, daemon=True).start()
threading.Thread(target=auto_ingest, daemon=True).start()
threading.Thread(target=track_ip_connections, daemon=True).start()

# Launch GUI
launch_gui()

