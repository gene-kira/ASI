from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit, QLineEdit, QPushButton, QHBoxLayout
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from config import PERSONAS, MAX_LOG_LINES
from scanner import check_outbound_risk, scan_payload_for_risks
from vault import update_vault
from mutation import narrate_event

class TrafficPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🌍 Global Traffic & Destination Dashboard")
        self.setStyleSheet("background-color: #000a1a; color: #00ffcc;")
        self.setGeometry(950, 100, 800, 600)
        font = QFont("OCR A Extended", 10)

        layout = QVBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP")
        self.ip_input.setFont(font)
        self.ip_action = QComboBox()
        self.ip_action.addItems(["allow", "block"])
        self.ip_action.setFont(font)
        self.ip_btn = QPushButton("Update Vault")
        self.ip_btn.setFont(font)
        self.ip_btn.clicked.connect(self.update_ip_vault)

        ip_layout = QHBoxLayout()
        ip_layout.addWidget(self.ip_input)
        ip_layout.addWidget(self.ip_action)
        ip_layout.addWidget(self.ip_btn)
        layout.addWidget(QLabel("🔐 IP Vault Control"))
        layout.addLayout(ip_layout)

        self.traffic_console = QTextEdit()
        self.traffic_console.setFont(font)
        self.traffic_console.setReadOnly(True)
        layout.addWidget(QLabel("📡 All Traffic Log"))
        layout.addWidget(self.traffic_console)

        self.geo_label = QLabel("🌍 GeoTrace: [Initializing...]")
        self.geo_label.setFont(font)
        layout.addWidget(self.geo_label)

        self.persona_selector = QComboBox()
        self.persona_selector.addItems(PERSONAS)
        self.persona_selector.setFont(font)
        layout.addWidget(QLabel("🧬 Persona Overlay"))
        layout.addWidget(self.persona_selector)

        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan_traffic)
        self.timer.start(5000)

    def update_ip_vault(self):
        ip = self.ip_input.text().strip()
        action = self.ip_action.currentText()
        if ip:
            persona = self.persona_selector.currentText()
            update_vault(ip, action)
            msg = narrate_event(ip, f"vault_{action}", "updated", persona)
            self.traffic_console.append(msg)

    def scan_traffic(self):
        try:
            ip, country = check_outbound_risk()
            domain = "ads.google.com"
            decision = scan_payload_for_risks(ip, domain)
            self.geo_label.setText(f"🌍 GeoTrace: {ip} → {country} [{decision.upper()}]")
            persona = self.persona_selector.currentText()
            msg = narrate_event(domain, decision.upper(), f"{ip} → {country}", persona)
            self.traffic_console.append(msg)

            if self.traffic_console.document().blockCount() > MAX_LOG_LINES:
                self.traffic_console.clear()
        except Exception as e:
            self.traffic_console.append(f"⚠️ Traffic scan error: {str(e)}")
