import sys
import time
import threading
import random
from datetime import datetime, timedelta
import psutil
import socket
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QListWidget, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QTabWidget
)
from PyQt5.QtCore import Qt, QTimer

# ─────────────────────────────────────────────
# 🧠 Core Structures
# ─────────────────────────────────────────────
threats = []
codex_rules = {
    "telemetry_retention": 30,
    "personal_retention": 86400,
    "backdoor_retention": 3,
    "ghost_sync_detected": False
}
personas = ["ThreatHunter", "Compliance Auditor", "Ghost Sync"]
allowed_ips = set()
blocked_ips = set()
allowed_countries = set()
blocked_countries = set()

# ─────────────────────────────────────────────
# 📜 Symbolic Narration
# ─────────────────────────────────────────────
def narrate(event):
    print(f"[PROPHECY] {event}")

# ─────────────────────────────────────────────
# 🧬 Codex Mutation Logic
# ─────────────────────────────────────────────
def mutate_codex(trigger):
    if trigger == "ghost_sync":
        codex_rules["telemetry_retention"] = max(10, codex_rules["telemetry_retention"] - 5)
        codex_rules["ghost_sync_detected"] = True
        threats.append(["phantom node", "Ghost Sync", "Unknown", codex_rules["telemetry_retention"], "Pending"])
        narrate("Ghost sync detected. Codex mutated. Phantom node added.")

# ─────────────────────────────────────────────
# 🕸️ Swarm Sync Simulation
# ─────────────────────────────────────────────
def simulate_swarm_sync():
    narrate("The nodes whispered. The prophecy aligned.")
    mutate_codex("ghost_sync")

# ─────────────────────────────────────────────
# 🎭 Persona Injection
# ─────────────────────────────────────────────
def inject_persona(entropy_level):
    if entropy_level > 0.7:
        persona = personas[int(entropy_level * 10) % len(personas)]
        narrate(f"Persona {persona} injected into threat matrix.")
        return persona
    return "None"

# ─────────────────────────────────────────────
# 🌐 Country/IP Filter
# ─────────────────────────────────────────────
def quarantine_origin(ip, country):
    if ip in allowed_ips or country in allowed_countries:
        return
    if ip in blocked_ips or country in blocked_countries:
        threats.append([ip, "Blocked", country, "-", "Blocked"])
        narrate(f"{ip} from {country} blocked by codex.")
        return

    def auto_block():
        blocked_ips.add(ip)
        blocked_countries.add(country)
        threats.append([ip, "Auto-Blocked", country, "-", "Blocked"])
        narrate(f"{ip} from {country} auto-blocked after 5s quarantine.")

    threading.Timer(5, auto_block).start()

# ─────────────────────────────────────────────
# 🔍 Real-Time Threat Ingestion
# ─────────────────────────────────────────────
def classify_live_threats():
    for proc in psutil.process_iter(['pid', 'name']):
        name = proc.info['name']
        if name and any(term in name.lower() for term in ["telemetry", "track", "sync", "update"]):
            origin_ip = socket.gethostbyname(socket.gethostname())
            origin_country = "Unknown"
            retention = codex_rules["telemetry_retention"]
            threats.append([name, "Telemetry", origin_country, retention, "Pending"])
            quarantine_origin(origin_ip, origin_country)
            narrate(f"Telemetry threat classified: {name}")

# ─────────────────────────────────────────────
# 🔒 Purge Logic
# ─────────────────────────────────────────────
def purge_expired_data():
    for threat in threats:
        if threat[4] == "Pending":
            retention = threat[3]
            if isinstance(retention, int) and retention < 30:
                threat[4] = "Purged"
                narrate(f"{threat[0]} purged by codex logic.")

# ─────────────────────────────────────────────
# 🖥️ GUI Construction
# ─────────────────────────────────────────────
class ASIGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASI Protection Shell vΩ.4")
        self.setGeometry(100, 100, 1100, 650)
        self.init_ui()
        self.start_defense_cycle()

    def init_ui(self):
        layout = QVBoxLayout()

        # Threat Matrix Table
        self.threat_table = QTableWidget(0, 5)
        self.threat_table.setHorizontalHeaderLabels(["Threat", "Type", "Origin", "Retention", "Status"])
        layout.addWidget(QLabel("🔬 Threat Matrix"))
        layout.addWidget(self.threat_table)

        # Persona Status
        self.persona_label = QLabel("🎭 Persona: None")
        layout.addWidget(self.persona_label)

        # Country/IP Filter Tabs
        self.filter_tabs = QTabWidget()
        self.allow_list = QListWidget()
        self.block_list = QListWidget()

        self.filter_tabs.addTab(self.allow_list, "✅ Allow List")
        self.filter_tabs.addTab(self.block_list, "🚫 Block List")
        layout.addWidget(self.filter_tabs)

        # Controls
        control_layout = QHBoxLayout()
        self.country_combo = QComboBox()
        self.country_combo.addItems(["RU", "CN", "IR", "BR", "NG"])
        self.allow_button = QPushButton("Add to Allow")
        self.block_button = QPushButton("Add to Block")
        self.allow_button.clicked.connect(self.add_to_allow)
        self.block_button.clicked.connect(self.add_to_block)
        control_layout.addWidget(QLabel("🌐 Country/IP Control"))
        control_layout.addWidget(self.country_combo)
        control_layout.addWidget(self.allow_button)
        control_layout.addWidget(self.block_button)
        layout.addLayout(control_layout)

        # Sync Button
        self.sync_button = QPushButton("🕸️ Simulate Swarm Sync")
        self.sync_button.clicked.connect(self.sync_swarm)
        layout.addWidget(self.sync_button)

        self.setLayout(layout)

    def start_defense_cycle(self):
        self.timer = QTimer()
        self.timer.timeout.connect(self.defense_tick)
        self.timer.start(5000)  # Every 5 seconds

        threading.Timer(30, self.symbolic_alert).start()

    def defense_tick(self):
        classify_live_threats()
        purge_expired_data()
        self.update_threat_table()
        entropy = random.random()
        persona = inject_persona(entropy)
        self.persona_label.setText(f"🎭 Persona: {persona}")

    def update_threat_table(self):
        self.threat_table.setRowCount(0)
        for threat in threats:
            row = self.threat_table.rowCount()
            self.threat_table.insertRow(row)
            for col, value in enumerate(threat):
                self.threat_table.setItem(row, col, QTableWidgetItem(str(value)))

    def add_to_allow(self):
        item = self.country_combo.currentText()
        allowed_countries.add(item)
        self.allow_list.addItem(item)
        narrate(f"{item} added to allow list.")

    def add_to_block(self):
        item = self.country_combo.currentText()
        blocked_countries.add(item)
        self.block_list.addItem(item)
        narrate(f"{item} added to block list.")

    def sync_swarm(self):
        simulate_swarm_sync()
        self.update_threat_table()

    def symbolic_alert(self):
        narrate("⚠️ Entropy threshold reached. Codex escalation advised.")
        threats.append(["Entropy Alert", "System", "Local", "-", "Advisory"])
        self.update_threat_table()

# ─────────────────────────────────────────────
# 🚀 Launch GUI
# ─────────────────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    shell = ASIGUI()
    shell.show()
    sys.exit(app.exec_())
