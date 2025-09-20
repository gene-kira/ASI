import subprocess, sys, random, time

# Autoloader
for pkg in ["PyQt5", "psutil", "scapy"]:
    try: __import__(pkg)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])

import psutil
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QSlider, QTextEdit, QGridLayout, QLineEdit
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal

try:
    from scapy.all import sniff
    PACKET_ENABLED = True
except ImportError:
    PACKET_ENABLED = False

class PacketSniffer(QThread):
    packet_signal = pyqtSignal(str)
    def run(self): sniff(prn=lambda pkt: self.packet_signal.emit(pkt.summary()), store=False)

class EchoNull(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EchoNull v3: Enhanced Tactical Shell")
        self.setStyleSheet("background:#111; color:#0f0; font-family:OCR A Std;")
        self.resize(1100, 750)
        self.polarity, self.lineage, self.swarm = 0, [], {}
        self.consensus = None

        layout = QVBoxLayout()
        layout.addWidget(self.label("⚡ EchoNull Interface", 24, "#f00"))
        layout.addLayout(self.controls())
        self.radar = self.label("Polarity Radar: [0]", 18)
        layout.addWidget(self.radar)
        self.log = self.textbox("#000")
        self.status = self.textbox("#112")
        layout.addWidget(self.log)
        layout.addWidget(self.status)

        if PACKET_ENABLED:
            self.packets = self.textbox("#113")
            layout.addWidget(self.packets)
            self.sniffer = PacketSniffer()
            self.sniffer.packet_signal.connect(lambda s: self.packets.append(f"[PACKET] {s}"))
            self.sniffer.start()
        else:
            self.log.append("⚠️ Packet inspection disabled (scapy not found)")

        self.setLayout(layout)
        QTimer(self, timeout=self.telemetry).start(1000)

    def label(self, text, size=14, color="#0f0"):
        l = QLabel(text); l.setAlignment(Qt.AlignCenter)
        l.setStyleSheet(f"font-size:{size}px; color:{color}; padding:6px;")
        return l

    def textbox(self, bg):
        t = QTextEdit(); t.setReadOnly(True)
        t.setStyleSheet(f"background:{bg}; color:#0f0; font-size:12px;")
        return t

    def controls(self):
        grid = QGridLayout()
        self.dampen = QPushButton("🌀 Echo Veil"); self.dampen.setCheckable(True)
        self.dampen.clicked.connect(lambda: self.log.append(f"[CONTROL] Echo Veil {'ON' if self.dampen.isChecked() else 'OFF'}"))
        self.cancel = QPushButton("🌑 Shadow Glyph"); self.cancel.clicked.connect(self.cancel_polarity)
        self.quarantine = QPushButton("🔒 Vault"); self.quarantine.clicked.connect(self.quarantine_feedback)
        self.inertia = QSlider(Qt.Horizontal); self.inertia.setRange(0,10); self.inertia.setValue(5)
        self.manual = QLineEdit(); self.manual.setPlaceholderText("> command"); self.manual.returnPressed.connect(self.command)

        grid.addWidget(QLabel("Inertia:"), 0, 0)
        grid.addWidget(self.inertia, 0, 1)
        grid.addWidget(self.dampen, 1, 0)
        grid.addWidget(self.cancel, 1, 1)
        grid.addWidget(self.quarantine, 1, 2)
        grid.addWidget(self.manual, 2, 0, 1, 3)
        return grid

    def telemetry(self):
        cpu, mem = psutil.cpu_percent(), psutil.virtual_memory().percent
        net = psutil.net_io_counters().bytes_sent + psutil.net_io_counters().bytes_recv
        delta = int(cpu + mem + (net % 1000) / 100)
        if self.dampen.isChecked(): delta = int(delta * (1 - self.inertia.value() / 10))
        self.polarity += delta
        self.radar.setText(f"Polarity Radar: [{self.polarity}]")
        timestamp = time.strftime("%H:%M:%S")
        self.lineage.append(f"{timestamp} Δ {delta} → {self.polarity}")
        self.log.append(f"[{timestamp}] CPU:{cpu}% MEM:{mem}% NET:{net} → Δ {delta}")
        self.sync_swarm()
        if abs(self.polarity) > 200: self.quarantine_feedback()

    def sync_swarm(self):
        node = f"node{random.randint(1000,9999)}"
        hashval = hash(tuple(self.lineage[-5:]))
        self.swarm[node] = hashval
        if not self.consensus: self.consensus = hashval
        drift = [n for n,h in self.swarm.items() if h != self.consensus]
        self.status.clear()
        self.status.append(f"[SYNC] Consensus: {self.consensus}")
        self.status.append(f"[SYNC] Nodes: {len(self.swarm)}")
        if drift:
            self.status.append(f"⚠️ Drift Detected: {', '.join(drift)}")
            self.status.append("🔴 Visual Alert: Lineage fracture detected")
        else:
            self.status.append("✅ All nodes synchronized")

    def cancel_polarity(self):
        timestamp = time.strftime("%H:%M:%S")
        self.log.append(f"[{timestamp}] Shadow Glyph deployed → Cancel {self.polarity}")
        self.lineage.append(f"{timestamp} Canceled polarity {self.polarity}")
        self.polarity = 0; self.radar.setText("Polarity Radar: [0]")

    def quarantine_feedback(self):
        timestamp = time.strftime("%H:%M:%S")
        self.log.append(f"[{timestamp}] 🔒 Vault sealed rogue feedback")
        self.lineage.append(f"{timestamp} Quarantined polarity {self.polarity}")
        self.status.append("🔴 ALERT: Quarantine triggered")
        self.polarity = 0; self.radar.setText("Polarity Radar: [0]")

    def command(self):
        cmd = self.manual.text().strip().lower()
        if "quarantine" in cmd: self.quarantine_feedback()
        elif "cancel" in cmd: self.cancel_polarity()
        elif "echo" in cmd: self.dampen.toggle(); self.log.append("Echo Veil toggled")
        else: self.log.append(f"[COMMAND] Unknown: {cmd}")
        self.manual.clear()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EchoNull()
    window.show()
    sys.exit(app.exec_())

