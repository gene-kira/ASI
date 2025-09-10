# -*- coding: utf-8 -*-
import threading
import time
import random
from datetime import datetime

# Import all modules (assumes they are in the same directory or properly packaged)
from codex_mutator import CodexMutator
from swarm_sync import SwarmSync
from event_bus import EventBus
from persona_engine import PersonaEngine
from ingest_engine import IngestEngine
from country_filter import CountryFilter
from mythic_gui import MythicDefenseGUI

def start_node(node_id="Node-Ω"):
    # Initialize GUI
    gui = MythicDefenseGUI(node_id)
    
    # Initialize modules
    event_bus = EventBus()
    codex = CodexMutator()
    country_filter = CountryFilter(gui)
    ingest_engine = IngestEngine(gui, codex, event_bus, country_filter)
    persona_engine = PersonaEngine(gui, event_bus)
    swarm_sync = SwarmSync(codex)

    # Autonomous Loops
    def ingest_loop():
        while True:
            time.sleep(random.randint(5, 10))
            data_id = f"{node_id}_data_{int(time.time())}"
            content = random.choice([
                "backdoor: leaked credentials",
                "mac: 00:1B:44:11:3A:B7 ip: 192.168.1.1",
                "face scan, phone number, social security",
                "telemetry: real-time location",
                "origin: RU destination: US"
            ])
            ingest_engine.ingest(data_id, content)

    def persona_loop():
        while True:
            time.sleep(30)
            if random.random() > 0.7:
                log = persona_engine.inject()
                gui.event_log.insert("end", log + "\n")

    def sync_loop():
        while True:
            time.sleep(20)
            log = swarm_sync.simulate_sync()
            gui.event_log.insert("end", event_bus.log(log) + "\n")

    def mutation_loop():
        while True:
            time.sleep(15)
            codex.mutate(event_bus.events)

    # Start threads
    threading.Thread(target=ingest_loop, daemon=True).start()
    threading.Thread(target=persona_loop, daemon=True).start()
    threading.Thread(target=sync_loop, daemon=True).start()
    threading.Thread(target=mutation_loop, daemon=True).start()

    # Launch GUI
    gui.mainloop()

if __name__ == "__main__":
    start_node()

