import psutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from config import PERSONAS, MAX_LOG_LINES
from mutation import narrate_event

class PortMonitorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📡 Live Port Traffic Monitor")
        self.setStyleSheet("background-color: #001a00; color: #00ff00;")
        self.setGeometry(100, 750, 800, 400)
        font = QFont("OCR A Extended", 10)

        layout = QVBoxLayout()

        # Persona selector
        self.persona_selector = QComboBox()
        self.persona_selector.addItems(PERSONAS)
        self.persona_selector.setFont(font)
        layout.addWidget(QLabel("🧬 Persona Overlay"))
        layout.addWidget(self.persona_selector)

        # Console
        self.port_console = QTextEdit()
        self.port_console.setFont(font)
        self.port_console.setReadOnly(True)
        layout.addWidget(QLabel("🔍 Outbound Port Feed"))
        layout.addWidget(self.port_console)

        self.setLayout(layout)

        # Autonomous scan loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan_ports)
        self.timer.start(5000)

    def scan_ports(self):
        try:
            persona = self.persona_selector.currentText()
            self.port_console.append("\n🔄 Scanning outbound ports...")
            for conn in psutil.net_connections(kind='inet')[:100]:  # Limit to first 100
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    ip = conn.raddr.ip
                    port = conn.raddr.port
                    proto = "TCP" if conn.type == 1 else "UDP"
                    pid = conn.pid
                    msg = f"{proto} → {ip}:{port} [PID: {pid}]"
                    self.port_console.append(f"🧬 {msg}")
                    narrate_event(f"{ip}:{port}", "PORT_STREAM", f"PID {pid}", persona)

            if self.port_console.document().blockCount() > MAX_LOG_LINES:
                self.port_console.clear()
        except Exception as e:
            self.port_console.append(f"⚠️ Port scan error: {str(e)}")

