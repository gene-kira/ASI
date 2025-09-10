# main.py

import threading
import time
import socket
import os
from datetime import datetime
from cryptography.fernet import Fernet

# === CONFIGURATION ===
NODE_ID = "Node-Ω"
LOG_FILE_PATH = r"C:\MyDefenseNode\logs\system.log"
SENSOR_DIR = r"C:\MyDefenseNode\sensor_data"
NETWORK_PORT = 9000
SECRET_KEY = Fernet.generate_key()  # Store securely in production

# === MODULE IMPORTS ===
from mythic_gui import MythicDefenseGUI
from codex_mutator import CodexMutator
from event_bus import EventBus
from persona_engine import PersonaEngine
from ingest_engine import IngestEngine
from country_filter import CountryFilter
from genre_overlay import GenreOverlay
from persistent_memory import PersistentMemory
from node_registry import NodeRegistry
from distributed_sync import DistributedSyncBus
from glyph_overlay import GlyphOverlay
from swarm_dashboard import SwarmDashboard
from swarm_voting import SwarmVoting

# === INITIALIZE COMPONENTS ===
registry = NodeRegistry()
gui = MythicDefenseGUI(NODE_ID)
event_bus = EventBus()
codex = CodexMutator()
memory = PersistentMemory()
country_filter = CountryFilter(gui)
ingest_engine = IngestEngine(gui, codex, event_bus, country_filter)
persona_engine = PersonaEngine(gui, event_bus)
overlay = GenreOverlay()
glyph = GlyphOverlay()
sync_bus = DistributedSyncBus(NODE_ID, codex, registry, SECRET_KEY)
dashboard = SwarmDashboard(registry)
voting = SwarmVoting(registry)

# === INGEST: SYSTEM LOG ===
def log_file_ingest():
    try:
        with open(LOG_FILE_PATH, "r") as f:
            f.seek(0, 2)
            while True:
                line = f.readline()
                if line:
                    data_id = f"{NODE_ID}_log_{int(time.time())}"
                    ingest_engine.ingest(data_id, line.strip())
                else:
                    time.sleep(0.5)
    except Exception as e:
        print(f"[ERROR] Log file ingest failed: {e}")

# === INGEST: NETWORK STREAM ===
def network_stream_ingest():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.bind(("0.0.0.0", NETWORK_PORT))
        s.listen(5)
        while True:
            conn, addr = s.accept()
            data = conn.recv(4096).decode("utf-8")
            if data:
                data_id = f"{NODE_ID}_net_{int(time.time())}"
                ingest_engine.ingest(data_id, data.strip())
    except Exception as e:
        print(f"[ERROR] Network stream ingest failed: {e}")

# === INGEST: SENSOR FEED ===
def sensor_feed_ingest():
    seen = set()
    try:
        while True:
            for fname in os.listdir(SENSOR_DIR):
                if fname not in seen:
                    seen.add(fname)
                    full_path = os.path.join(SENSOR_DIR, fname)
                    with open(full_path, "r") as f:
                        content = f.read()
                        data_id = f"{NODE_ID}_sensor_{int(time.time())}"
                        ingest_engine.ingest(data_id, content.strip())
            time.sleep(1)
    except Exception as e:
        print(f"[ERROR] Sensor feed ingest failed: {e}")

# === PERSONA LOOP ===
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

# === CODEX MUTATION LOOP ===
def mutation_loop():
    while True:
        time.sleep(15)
        codex.mutate(event_bus.events)
        memory.record_codex(codex.export_codex())

# === SWARM SYNC LOOP ===
def sync_loop():
    while True:
        log = sync_bus.sync()
        overlay.evaluate(codex.codex)
        theme = overlay.get_theme()
        ingest_count = len(ingest_engine.memory_store)
        glyph.update(codex.codex, persona_engine.is_active(), ingest_count)
        registry.register(NODE_ID, {
            "codex": codex.export_codex(),
            "encrypted": sync_bus.crypto.encrypt_codex(codex.export_codex()),
            "glyph": glyph.render()
        })
        gui.title(f"{NODE_ID} [{theme}] {glyph.render()}")
        gui.event_log.insert("end", event_bus.log(log) + "\n")
        time.sleep(20)

# === DASHBOARD + VOTING LOOP ===
def dashboard_loop():
    while True:
        summary = dashboard.render_summary()
        top_threats = voting.get_top_threats()
        threat_report = "\n".join([f"{sig}: {votes}" for sig, votes in top_threats])
        ancestry = codex.export_ancestry()
        ancestry_log = "\n".join([f"{a['timestamp']} — {a['reason']}" for a in ancestry[-3:]])
        gui.event_log.insert("end", f"\n[SWARM DASHBOARD]\n{summary}\n\n[THREAT VOTING]\n{threat_report}\n\n[CODEX ANCESTRY]\n{ancestry_log}\n\n")
        time.sleep(60)

# === THREAD LAUNCH ===
threading.Thread(target=log_file_ingest, daemon=True).start()
threading.Thread(target=network_stream_ingest, daemon=True).start()
threading.Thread(target=sensor_feed_ingest, daemon=True).start()
threading.Thread(target=persona_loop, daemon=True).start()
threading.Thread(target=mutation_loop, daemon=True).start()
threading.Thread(target=sync_loop, daemon=True).start()
threading.Thread(target=dashboard_loop, daemon=True).start()

# === LAUNCH GUI ===
gui.mainloop()

