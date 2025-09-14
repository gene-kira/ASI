import psutil
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QTextEdit, QComboBox,
    QLineEdit, QPushButton, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
from config import PERSONAS, MAX_LOG_LINES
from mutation import narrate_event
from vault import load_vault

# 🔒 Glyph definitions
GLYPH_LOCKDOWNS = {
    "BlackSun": [80, 443, 53],       # HTTP, HTTPS, DNS
    "IronMask": "UDP",               # Quarantine all UDP
    "EchoSeal": "VAULT_ONLY",        # Allow only whitelisted ports
    "NullGlyph": "PURGE_ALL"         # Kill all outbound streams
}

class PortControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ Port Control Console")
        self.setStyleSheet("background-color: #0a0a0a; color: #00ffcc;")
        self.setGeometry(950, 750, 800, 500)
        font = QFont("OCR A Extended", 10)

        layout = QVBoxLayout()

        # Persona selector
        self.persona_selector = QComboBox()
        self.persona_selector.addItems(PERSONAS)
        self.persona_selector.setFont(font)
        layout.addWidget(QLabel("🧬 Persona Overlay"))
        layout.addWidget(self.persona_selector)

        # Glyph input
        glyph_layout = QHBoxLayout()
        self.glyph_input = QLineEdit()
        self.glyph_input.setPlaceholderText("Enter glyph (e.g. BlackSun)")
        self.glyph_input.setFont(font)
        self.glyph_btn = QPushButton("Trigger Glyph")
        self.glyph_btn.setFont(font)
        self.glyph_btn.clicked.connect(self.trigger_glyph)
        glyph_layout.addWidget(self.glyph_input)
        glyph_layout.addWidget(self.glyph_btn)
        layout.addWidget(QLabel("🔮 Glyph Console"))
        layout.addLayout(glyph_layout)

        # Console
        self.control_console = QTextEdit()
        self.control_console.setFont(font)
        self.control_console.setReadOnly(True)
        layout.addWidget(QLabel("📡 Port Lockdown Log"))
        layout.addWidget(self.control_console)

        self.setLayout(layout)

        # Autonomous scan loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan_ports)
        self.timer.start(5000)

    def scan_ports(self):
        try:
            self.control_console.append("\n🔄 Scanning open outbound ports...")
            for conn in psutil.net_connections(kind='inet')[:100]:
                if conn.status == 'ESTABLISHED' and conn.raddr:
                    ip = conn.raddr.ip
                    port = conn.raddr.port
                    proto = "TCP" if conn.type == 1 else "UDP"
                    pid = conn.pid
                    msg = f"{proto} → {ip}:{port} [PID: {pid}]"
                    self.control_console.append(f"🧬 {msg}")
                    narrate_event(f"{ip}:{port}", "PORT_ACTIVE", f"PID {pid}", "PortControl")

            if self.control_console.document().blockCount() > MAX_LOG_LINES:
                self.control_console.clear()
        except Exception as e:
            self.control_console.append(f"⚠️ Port scan error: {str(e)}")

    def trigger_glyph(self):
        glyph = self.glyph_input.text().strip()
        persona = self.persona_selector.currentText()
        lockdown = GLYPH_LOCKDOWNS.get(glyph)

        if not lockdown:
            self.control_console.append(f"❌ Unknown glyph: {glyph}")
            return

        self.control_console.append(f"\n🔒 Glyph triggered: {glyph}")
        vault = load_vault()

        try:
            for conn in psutil.net_connections(kind='inet')[:100]:
                if conn.status != 'ESTABLISHED' or not conn.raddr:
                    continue

                ip = conn.raddr.ip
                port = conn.raddr.port
                proto = "TCP" if conn.type == 1 else "UDP"
                pid = conn.pid

                # Lockdown logic
                if isinstance(lockdown, list) and port in lockdown:
                    psutil.Process(pid).terminate()
                    msg = f"🔒 {glyph} → Terminated {proto} {ip}:{port} [PID {pid}]"
                    self.control_console.append(msg)
                    narrate_event(f"{ip}:{port}", f"{glyph}_LOCKDOWN", f"PID {pid}", persona)

                elif lockdown == "UDP" and proto == "UDP":
                    psutil.Process(pid).terminate()
                    msg = f"🔒 {glyph} → Quarantined UDP {ip}:{port} [PID {pid}]"
                    self.control_console.append(msg)
                    narrate_event(f"{ip}:{port}", f"{glyph}_QUARANTINE", f"PID {pid}", persona)

                elif lockdown == "VAULT_ONLY":
                    if ip not in vault["allow"]:
                        psutil.Process(pid).terminate()
                        msg = f"🔒 {glyph} → Blocked {proto} {ip}:{port} [Not in vault]"
                        self.control_console.append(msg)
                        narrate_event(f"{ip}:{port}", f"{glyph}_VAULT_BLOCK", f"PID {pid}", persona)

                elif lockdown == "PURGE_ALL":
                    psutil.Process(pid).terminate()
                    msg = f"🧨 {glyph} → Purged {proto} {ip}:{port} [PID {pid}]"
                    self.control_console.append(msg)
                    narrate_event(f"{ip}:{port}", f"{glyph}_PURGE", f"PID {pid}", persona)

            self.control_console.append(f"✅ Glyph {glyph} executed.")
        except Exception as e:
            self.control_console.append(f"⚠️ Glyph error: {str(e)}")
