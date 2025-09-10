# main.py

import threading
import time
import socket
import os
from datetime import datetime

# === Module Imports ===
from mythic_gui import MythicDefenseGUI
from codex_mutator import CodexMutator
from event_bus import EventBus
from persona_engine import PersonaEngine
from ingest_engine import IngestEngine
from country_filter import CountryFilter
from swarm_sync import SwarmSync
from genre_overlay import GenreOverlay
from persistent_memory import PersistentMemory
from node_registry import NodeRegistry
from distributed_sync import DistributedSyncBus

# === Node Initialization ===
node_id = "Node-Ω"
registry = NodeRegistry()

gui = MythicDefenseGUI(node_id)
event_bus = EventBus()
codex = CodexMutator()
memory = PersistentMemory()
country_filter = CountryFilter(gui)
ingest_engine = IngestEngine(gui, codex, event_bus, country_filter)
persona_engine = PersonaEngine(gui, event_bus)
overlay = GenreOverlay()
sync_bus = DistributedSyncBus(node_id, codex, registry)

# === Real-Time Ingest: System Log ===
def log_file_ingest():
    log_path = "/var/log/syslog"  # Adjust for Windows: "C:\\Logs\\system.log"
    try:
        with open(log_path, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    data_id = f"{node_id}_log_{int(time.time())}"
                    ingest_engine.ingest(data_id, line.strip())
                else:
                    time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR] Log file ingest failed: {e}")

# === Real-Time Ingest: Network Stream ===
def network_stream_ingest():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", 9000))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            data = conn.recv(4096).decode("utf-8")
            if data:
                data_id = f"{node_id}_net_{int(time.time())}"
                ingest_engine.ingest(data_id, data.strip())
    except Exception as e:
        print(f"[ERROR] Network stream ingest failed: {e}")

# === Real-Time Ingest: Sensor Feed ===
def sensor_feed_ingest():
    sensor_dir = "/path/to/sensor_data"  # Replace with actual sensor path
    seen = set()
    try:
        while True:
            for fname in os.listdir(sensor_dir):
                if fname not in seen:
                    seen.add(fname)
                    full_path = os.path.join(sensor_dir, fname)
                    with open(full_path, "r") as f:
                        content = f.read()
                        data_id = f"{node_id}_sensor_{int(time.time())}"
                        ingest_engine.ingest(data_id, content.strip())
            time.sleep(1)
    except Exception as e:
        print(f"[ERROR] Sensor feed ingest failed: {e}")

# === Persona Injection Loop ===
def persona_loop():
    while True:
        time.sleep(30)
        if not persona_engine.is_active():
            log = persona_engine.inject()
            gui.event_log.insert("end", log + "\n")
            memory.record_persona(log)
            time.sleep(10)
            log = persona_engine.deactivate()
            gui.event_log.insert("end", log + "\n")

# === Codex Mutation Loop ===
def mutation_loop():
    while True:
        time.sleep(15)
        codex.mutate(event_bus.events)
        memory.record_codex(codex.export_codex())

# === Swarm Sync Loop ===
def sync_loop():
    while True:
        log = sync_bus.sync()
        overlay.evaluate(codex.codex)
        theme = overlay.get_theme()
        gui.title(f"{node_id} [{theme}]")
        gui.event_log.insert("end", event_bus.log(log) + "\n")
        time.sleep(20)

# === Launch Threads ===
threading.Thread(target=log_file_ingest, daemon=True).start()
threading.Thread(target=network_stream_ingest, daemon=True).start()
threading.Thread(target=sensor_feed_ingest, daemon=True).start()
threading.Thread(target=persona_loop, daemon=True).start()
threading.Thread(target=mutation_loop, daemon=True).start()
threading.Thread(target=sync_loop, daemon=True).start()

# === Launch GUI ===
gui.mainloop()

