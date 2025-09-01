# main.py — VeilMind Nexus Launcher

import threading
import time
import tkinter as tk
from modules import (
    get_ip_telemetry,
    get_system_telemetry,
    fuse_telemetry,
    predictive_cloak,
    store_mutation,
    symbolic_memory,
    MagicBoxGUI
)

SWARM_ID = "VEILMIND-ZERO-TRUST-001"

def daemon_loop():
    while True:
        ip_data = get_ip_telemetry()
        sys_data = get_system_telemetry()
        fusion_data, emotion = fuse_telemetry(ip_data, sys_data)

        encoded, mutation_id = predictive_cloak(fusion_data, sys_data["Entropy_Pulse"], emotion)
        if encoded:
            store_mutation(encoded, mutation_id, emotion)

        time.sleep(5)

def launch_gui():
    root = tk.Tk()
    app = MagicBoxGUI(root)
    root.mainloop()

if __name__ == "__main__":
    print(f"[LAUNCH] VeilMind Nexus '{SWARM_ID}' initializing...")
    threading.Thread(target=daemon_loop, daemon=True).start()
    launch_gui()

