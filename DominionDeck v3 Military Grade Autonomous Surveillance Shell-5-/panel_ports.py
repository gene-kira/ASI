import psutil
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox, QLineEdit, QPushButton
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from config import PERSONAS, MAX_LOG_LINES
from mutation import narrate_event

# 🔒 Glyph definitions
GLYPH_LOCKDOWNS = {
    "BlackSun": [80, 443, 53],       # HTTP, HTTPS, DNS
    "IronMask": "UDP",               # Quarantine all UDP
    "EchoSeal": "VAULT_ONLY",        # Allow only whitelisted ports
    "NullGlyph": "PURGE_ALL"         # Kill all outbound streams
}

class PortMonitorPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("📡 Live Port Traffic Monitor")
        self.setStyleSheet("background-color: #001a00; color: #00ff00;")
        self.setGeometry(100, 750, 800, 500)
        font = QFont("OCR A Extended", 10)

        layout = QVBoxLayout()

        # Persona selector
        self.persona_selector = QComboBox()
        self.persona_selector.addItems(PERSONAS)
        self.persona_selector.setFont(font)
        layout.addWidget(QLabel("🧬 Persona Overlay"))
        layout.addWidget(self.persona_selector)

        # Glyph input
        self.glyph_input = QLineEdit()
        self.glyph_input.setPlaceholderText("Enter glyph (e.g. BlackSun)")
        self.glyph_input.setFont(font)
        self.glyph_btn = QPushButton("Trigger Glyph")
        self.glyph_btn.setFont(font)
        self.glyph_btn.clicked.connect(self.trigger_glyph)
        layout.addWidget(QLabel("🔮 Glyph Console"))
        layout.addWidget(self.glyph_input)
        layout.addWidget(self.glyph_btn)

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
            for conn in psutil.net_connections(kind='inet')[:100]:
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

    def trigger_glyph(self):
        glyph = self.glyph_input.text().strip()
        persona = self.persona_selector.currentText()
        if glyph not in GLYPH_LOCKDOWNS:
            self.port_console.append(f"❌ Unknown glyph: {glyph}")
            return

        self.port_console.append(f"\n🔒 Glyph triggered: {glyph}")
        lockdown = GLYPH_LOCKDOWNS[glyph]

        try:
            for conn in psutil.net_connections(kind='inet')[:100]:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    ip = conn.raddr.ip
                    port = conn.raddr.port
                    proto = "TCP" if conn.type == 1 else "UDP"
                    pid = conn.pid

                    # Apply lockdown logic
                    if isinstance(lockdown, list) and port in lockdown:
                        psutil.Process(pid).terminate()
                        msg = f"🔒 {glyph} → Terminated {proto} {ip}:{port} [PID {pid}]"
                        self.port_console.append(msg)
                        narrate_event(f"{ip}:{port}", f"{glyph}_LOCKDOWN", f"PID {pid}", persona)

                    elif lockdown == "UDP" and proto == "UDP":
                        psutil.Process(pid).terminate()
                        msg = f"🔒 {glyph} → Quarantined UDP {ip}:{port} [PID {pid}]"
                        self.port_console.append(msg)
                        narrate_event(f"{ip}:{port}", f"{glyph}_QUARANTINE", f"PID {pid}", persona)

                    elif lockdown == "PURGE_ALL":
                        psutil.Process(pid).terminate()
                        msg = f"🧨 {glyph} → Purged {proto} {ip}:{port} [PID {pid}]"
                        self.port_console.append(msg)
                        narrate_event(f"{ip}:{port}", f"{glyph}_PURGE", f"PID {pid}", persona)

            self.port_console.append(f"✅ Glyph {glyph} executed.")
        except Exception as e:
            self.port_console.append(f"⚠️ Glyph error: {str(e)}")

