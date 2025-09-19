# ┌────────────────────────────────────────────┐
# │ EchoNull Autoloader: Tactical Dependency Check │
# └────────────────────────────────────────────┘
import subprocess
import sys

required_packages = ["PyQt5"]
for pkg in required_packages:
    try:
        __import__(pkg)
    except ImportError:
        print(f"[EchoNull] Missing package: {pkg} → Installing...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        print(f"[EchoNull] {pkg} installed successfully.")

# ┌────────────────────────────────────────────┐
# │ EchoNull GUI: Mutation-Aware Suppression Core │
# └────────────────────────────────────────────┘
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QHBoxLayout, QSlider, QTextEdit, QGridLayout, QLineEdit
)
from PyQt5.QtCore import Qt, QTimer

class EchoNull(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EchoNull: Mutation-Aware Polarity Suppression Core")
        self.setStyleSheet("background-color: #1a1a1a; color: #00ff00; font-family: OCR A Std;")
        self.resize(1000, 650)

        self.polarity = 0
        self.mutation_log = []
        self.lineage = []

        layout = QVBoxLayout()
        layout.addWidget(self.create_header())
        layout.addLayout(self.create_controls())
        layout.addWidget(self.create_radar())
        layout.addWidget(self.create_log())
        layout.addWidget(self.create_lineage_tracker())
        self.setLayout(layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.simulate_data_stream)
        self.timer.start(1000)

    def create_header(self):
        label = QLabel("⚡ EchoNull Tactical Interface")
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
        self.manual_input.setPlaceholderText("> quarantine --id 7A3F")
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

    def simulate_data_stream(self):
        incoming = random.randint(-10, 10)
        inertia = self.inertia_slider.value()

        if self.dampen_btn.isChecked():
            incoming = int(incoming * (1 - inertia / 10))

        self.polarity += incoming
        self.radar.setText(f"Polarity Radar: [{self.polarity}]")

        entry = f"Incoming polarity: {incoming} → Total: {self.polarity}"
        self.mutation_log.append(entry)
        self.lineage.append(f"Δ {incoming} @ polarity {self.polarity}")
        self.log.append(entry)

        if abs(self.polarity) > 20:
            self.log.append("⚠️ Volatile polarity detected!")

        self.update_lineage()

    def update_lineage(self):
        self.lineage_display.clear()
        for item in self.lineage[-10:]:
            self.lineage_display.append(item)

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

