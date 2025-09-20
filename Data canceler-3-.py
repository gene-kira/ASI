# ┌────────────────────────────────────────────┐
# │ EchoNull v2: Swarm-Synced Quantum Drift Core │
# └────────────────────────────────────────────┘
import subprocess
import sys

# Autoloader for required packages
required_packages = ["PyQt5", "psutil"]
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        print(f"[EchoNull] Missing package: {pkg} → Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print(f"[EchoNull] {pkg} installed successfully.")

import psutil
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QSlider, QTextEdit, QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer

class EchoNull(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EchoNull v2: Swarm-Synced Quantum Drift Core")
        self.setStyleSheet("background-color: #1a1a1a; color: #00ff00; font-family: OCR A Std;")
        self.resize(1100, 700)

        self.polarity = 0
        self.lineage = []
        self.swarm_nodes = {}
        self.consensus_hash = None

        layout = QVBoxLayout()
        layout.addWidget(self.create_header())
        layout.addLayout(self.create_controls())
        layout.addWidget(self.create_radar())
        layout.addWidget(self.create_log())
        layout.addWidget(self.create_lineage_tracker())
        layout.addWidget(self.create_swarm_tracker())
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.monitor_telemetry)
        self.timer.start(1000)

    def create_header(self):
        label = QLabel("⚡ EchoNull v2: Tactical Sentinel Interface")
        label.setStyleSheet("font-size: 24px; font-weight: bold; color: #ff0000;")
        label.setAlignment(Qt.AlignCenter)
        return label

    def create_controls(self):
        controls = QGridLayout()

        self.dampen_btn = QPushButton("🌀 Echo Veil")
        self.dampen_btn.setCheckable(True)
        self.dampen_btn.clicked.connect(self.toggle_dampening)

        self.cancel_btn = QPushButton("🌑 Shadow Glyph")
        self.cancel_btn.clicked.connect(self.cancel_polarity)

        self.quarantine_btn = QPushButton("🔒 Containment Vault")
        self.quarantine_btn.clicked.connect(self.quarantine_feedback)

        self.inertia_slider = QSlider(Qt.Horizontal)
        self.inertia_slider.setMinimum(0)
        self.inertia_slider.setMaximum(10)
        self.inertia_slider.setValue(5)
        self.inertia_slider.setStyleSheet("background-color: #333;")

        self.manual_input = QLineEdit()
        self.manual_input.setPlaceholderText("> quarantine --id node7A3F")
        self.manual_input.returnPressed.connect(self.manual_command)

        controls.addWidget(QLabel("Inertia Level:"), 0, 0)
        controls.addWidget(self.inertia_slider, 0, 1)
        controls.addWidget(self.dampen_btn, 1, 0)
        controls.addWidget(self.cancel_btn, 1, 1)
        controls.addWidget(self.quarantine_btn, 1, 2)
        controls.addWidget(self.manual_input, 2, 0, 1, 3)

        return controls

    def create_radar(self):
        self.radar = QLabel("Polarity Radar: [0]")
        self.radar.setStyleSheet("font-size: 18px; padding: 10px;")
        self.radar.setAlignment(Qt.AlignCenter)
        return self.radar

    def create_log(self):
        self.log = QTextEdit()
        self.log.setReadOnly(True)
        self.log.setStyleSheet("background-color: #000; color: #00ff00;")
        return self.log

    def create_lineage_tracker(self):
        self.lineage_display = QTextEdit()
        self.lineage_display.setReadOnly(True)
        self.lineage_display.setStyleSheet("background-color: #111; color: #00ffaa; font-size: 12px;")
        self.lineage_display.setPlaceholderText("Mutation Ancestry Tracker")
        return self.lineage_display

    def create_swarm_tracker(self):
        self.swarm_display = QTextEdit()
        self.swarm_display.setReadOnly(True)
        self.swarm_display.setStyleSheet("background-color: #111; color: #ffcc00; font-size: 12px;")
        self.swarm_display.setPlaceholderText("Swarm Sync Status")
        return self.swarm_display

    def monitor_telemetry(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        polarity_input = int(cpu + mem + (net % 1000) / 100)

        inertia = self.inertia_slider.value()
        if self.dampen_btn.isChecked():
            polarity_input = int(polarity_input * (1 - inertia / 10))

        self.polarity += polarity_input
        self.radar.setText(f"Polarity Radar: [{self.polarity}]")

        entry = f"Telemetry → CPU:{cpu}% MEM:{mem}% NET:{net} → Δ {polarity_input} → Total: {self.polarity}"
        self.lineage.append(entry)
        self.log.append(entry)

        self.update_lineage()
        self.update_swarm_sync()

        if abs(self.polarity) > 200:
            self.log.append("⚠️ Quantum Drift Detected → Initiating Containment")
            self.quarantine_feedback()

    def update_lineage(self):
        self.lineage_display.clear()
        for item in self.lineage[-10:]:
            self.lineage_display.append(item)

    def update_swarm_sync(self):
        node_id = f"node{random.randint(1000,9999)}"
        ancestry_hash = hash(tuple(self.lineage[-5:]))
        self.swarm_nodes[node_id] = ancestry_hash

        if self.consensus_hash is None:
            self.consensus_hash = ancestry_hash

        drift_nodes = [nid for nid, h in self.swarm_nodes.items() if h != self.consensus_hash]
        self.swarm_display.clear()
        self.swarm_display.append(f"Consensus Hash: {self.consensus_hash}")
        self.swarm_display.append(f"Active Nodes: {len(self.swarm_nodes)}")
        if drift_nodes:
            self.swarm_display.append(f"⚠️ Drift Detected in Nodes: {', '.join(drift_nodes)}")
        else:
            self.swarm_display.append("✅ All nodes in sync")

    def toggle_dampening(self):
        state = "ON" if self.dampen_btn.isChecked() else "OFF"
        self.log.append(f"🌀 Echo Veil toggled {state}")

    def cancel_polarity(self):
        self.log.append(f"🌑 Shadow Glyph deployed → Canceling polarity {self.polarity}")
        self.lineage.append(f"Shadow Glyph neutralized polarity {self.polarity}")
        self.polarity = 0
        self.radar.setText(f"Polarity Radar: [0]")
        self.update_lineage()

    def quarantine_feedback(self):
        self.log.append("🔒 Containment Vault activated → Isolating rogue feedback")
        self.lineage.append(f"Quarantine shell sealed polarity {self.polarity}")
        self.polarity = 0
        self.radar.setText(f"Polarity Radar: [0]")
        self.update_lineage()

    def manual_command(self):
        cmd = self.manual_input.text().strip()
        if "quarantine" in cmd:
            self.quarantine_feedback()
            self.log.append(f"Manual command executed: {cmd}")
        else:
            self.log.append(f"Unknown command: {cmd}")
        self.manual_input.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EchoNull()
    window.show()
    sys.exit(app.exec_())

