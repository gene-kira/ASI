# ingest_engine.py

import threading
import time
from datetime import datetime

class IngestEngine:
    def __init__(self, gui, codex, event_bus, country_filter):
        self.gui = gui
        self.codex = codex
        self.event_bus = event_bus
        self.country_filter = country_filter
        self.memory_store = {}

    def ingest(self, data_id, content):
        """
        Classifies and ingests data. If allowed, stores and schedules purge.
        """
        category = self.classify(content)
        if not self.country_filter.allowed(content):
            log = self.event_bus.log(f"[BLOCKED] Country filter rejected {data_id}")
            self.gui.event_log.insert("end", log + "\n")
            return

        self.memory_store[data_id] = {
            "content": content,
            "timestamp": datetime.now(),
            "category": category
        }

        self.gui.ingest_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] Ingested {data_id} as {category.upper()}\n")
        log = self.event_bus.log(f"[INGEST] {data_id} classified as {category.upper()}")
        self.gui.event_log.insert("end", log + "\n")

        threading.Thread(target=self.schedule_purge, args=(data_id, category), daemon=True).start()

    def classify(self, content):
        """
        Determines the category of incoming data.
        """
        content = content.lower()
        if any(tag in content for tag in ["face", "finger", "bio", "phone", "address", "license", "social"]):
            return "personal"
        elif "telemetry" in content:
            return "telemetry"
        elif "mac" in content or "ip" in content:
            return "mac_ip"
        elif "backdoor" in content:
            return "backdoor"
        return "general"

    def schedule_purge(self, data_id, category):
        """
        Waits for the codex-defined retention period, then purges the data.
        """
        delay = self.codex.get_purge_delay(category)
        time.sleep(delay)

        if data_id in self.memory_store:
            del self.memory_store[data_id]
            self.gui.threat_log.insert("end", f"[{datetime.now().strftime('%H:%M:%S')}] PURGED {data_id} ({category.upper()})\n")
            log = self.event_bus.log(f"[PURGE] {data_id} destroyed after {delay}s")
            self.gui.event_log.insert("end", log + "\n")

