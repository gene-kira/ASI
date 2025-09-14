from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QComboBox, QTextEdit
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from config import PERSONAS, BLOCKED_COUNTRIES, MAX_LOG_LINES
from scanner import check_outbound_risk, scan_payload_for_risks
from mutation import narrate_event

class ThreatPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ High-Threat Surveillance Console")
        self.setStyleSheet("background-color: #1a0000; color: #ff4444;")
        self.setGeometry(100, 100, 800, 400)
        font = QFont("OCR A Extended", 10)

        layout = QVBoxLayout()
        self.persona_selector = QComboBox()
        self.persona_selector.addItems(PERSONAS)
        self.persona_selector.setFont(font)
        layout.addWidget(QLabel("🧬 Persona Overlay"))
        layout.addWidget(self.persona_selector)

        self.threat_console = QTextEdit()
        self.threat_console.setFont(font)
        self.threat_console.setReadOnly(True)
        layout.addWidget(QLabel("🚨 Blocked Traffic Feed"))
        layout.addWidget(self.threat_console)

        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan_threats)
        self.timer.start(5000)

    def scan_threats(self):
        try:
            persona = self.persona_selector.currentText()
            ip, country = check_outbound_risk()
            domain = "ads.google.com"
            decision = scan_payload_for_risks(ip, domain)

            if country in BLOCKED_COUNTRIES or decision == "block":
                msg = narrate_event(domain, "BLOCKED", f"{ip} → {country}", persona)
                self.threat_console.append(msg)

            if self.threat_console.document().blockCount() > MAX_LOG_LINES:
                self.threat_console.clear()
        except Exception as e:
            self.threat_console.append(f"⚠️ Threat scan error: {str(e)}")

