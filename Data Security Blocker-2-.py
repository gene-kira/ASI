import sys, random, socket, threading, psutil
from PyQt5.QtWidgets import *
from PyQt5.QtCore import QTimer

# ─── Codex State ─────────────────────────────
threats, allowed_ips, blocked_ips = [], set(), set()
allowed_countries, blocked_countries = set(), set()
shell = None

def narrate(msg): print(f"[PROPHECY] {msg}")

# ─── Threat Ingestion ────────────────────────
def ingest_threats():
    for p in psutil.process_iter(['name']):
        name = p.info['name']
        if name and any(x in name.lower() for x in ["telemetry", "track", "sync"]):
            ip = socket.gethostbyname(socket.gethostname())
            threats.append([name, "Telemetry", "Unknown", 30, "Pending"])
            quarantine(ip, "Unknown")
            narrate(f"Threat classified: {name}")

# ─── Auto-Block Logic ────────────────────────
def quarantine(ip, country):
    if ip in allowed_ips or country in allowed_countries: return
    if ip in blocked_ips or country in blocked_countries:
        threats.append([ip, "Blocked", country, "-", "Blocked"])
        return
    def block():
        blocked_ips.add(ip); blocked_countries.add(country)
        threats.append([ip, "Auto-Blocked", country, "-", "Blocked"])
        narrate(f"{ip} auto-blocked.")
        if shell: shell.block_list.addItem(f"{ip} ({country})"); shell.refresh()
    threading.Timer(5, block).start()

# ─── GUI Shell ───────────────────────────────
class ASIShell(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASI Shell vΩ")
        self.setGeometry(100, 100, 1100, 700)
        self.build_gui()
        QTimer().singleShot(30000, self.symbolic_alert)
        self.timer = QTimer(); self.timer.timeout.connect(self.tick); self.timer.start(5000)

    def build_gui(self):
        L = QVBoxLayout()
        self.threats = QTableWidget(0, 5); self.threats.setHorizontalHeaderLabels(["Threat", "Type", "Origin", "Retention", "Status"])
        self.persona = QLabel("🎭 Persona: None")
        self.allow_list, self.block_list = QListWidget(), QListWidget()
        self.country_input, self.ip_input = QLineEdit(), QLineEdit()
        self.country_input.setPlaceholderText("Country code"); self.ip_input.setPlaceholderText("IP address")
        self.allow_btn = QPushButton("Allow"); self.block_btn = QPushButton("Block")
        self.allow_btn.clicked.connect(self.add_allow); self.block_btn.clicked.connect(self.add_block)
        self.live_ips = QListWidget()

        L.addWidget(QLabel("🔬 Threat Matrix")); L.addWidget(self.threats)
        L.addWidget(self.persona)
        tabs = QTabWidget(); tabs.addTab(self.allow_list, "✅ Allow"); tabs.addTab(self.block_list, "🚫 Block")
        L.addWidget(tabs)
        row = QHBoxLayout(); row.addWidget(self.country_input); row.addWidget(self.ip_input)
        row.addWidget(self.allow_btn); row.addWidget(self.block_btn); L.addLayout(row)
        L.addWidget(QLabel("🔗 Allowed IP Connections")); L.addWidget(self.live_ips)
        sync_btn = QPushButton("🕸️ Sync"); sync_btn.clicked.connect(self.sync); L.addWidget(sync_btn)
        self.setLayout(L)

    def tick(self):
        ingest_threats()
        self.refresh()
        self.track_ips()
        self.persona.setText(f"🎭 Persona: {random.choice(['None','ThreatHunter','Ghost Sync'])}")

    def refresh(self):
        self.threats.setRowCount(0)
        for t in threats:
            row = self.threats.rowCount(); self.threats.insertRow(row)
            for i, val in enumerate(t): self.threats.setItem(row, i, QTableWidgetItem(str(val)))

    def track_ips(self):
        self.live_ips.clear()
        for c in psutil.net_connections(kind='tcp'):
            if c.raddr and c.raddr.ip in allowed_ips:
                self.live_ips.addItem(f"{c.raddr.ip}:{c.raddr.port}")

    def add_allow(self):
        c, ip = self.country_input.text().strip(), self.ip_input.text().strip()
        if c: allowed_countries.add(c); self.allow_list.addItem(f"Country: {c}"); narrate(f"{c} allowed.")
        if ip: allowed_ips.add(ip); self.allow_list.addItem(f"IP: {ip}"); narrate(f"{ip} allowed.")

    def add_block(self):
        c, ip = self.country_input.text().strip(), self.ip_input.text().strip()
        if c: blocked_countries.add(c); self.block_list.addItem(f"Country: {c}"); narrate(f"{c} blocked.")
        if ip: blocked_ips.add(ip); self.block_list.addItem(f"IP: {ip}"); narrate(f"{ip} blocked.")

    def sync(self):
        threats.append(["phantom node", "Ghost Sync", "Unknown", 25, "Pending"])
        narrate("Codex sync triggered."); self.refresh()

    def symbolic_alert(self):
        threats.append(["Entropy Alert", "System", "Local", "-", "Advisory"])
        narrate("⚠️ Codex escalation advised."); self.refresh()

# ─── Launch ──────────────────────────────────
if __name__ == "__main__":
    app = QApplication(sys.argv)
    shell = ASIShell(); shell.show()
    sys.exit(app.exec_())
