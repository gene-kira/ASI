import subprocess, sys, importlib, datetime, json, os, requests
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton,
    QComboBox, QTextEdit, QLineEdit, QHBoxLayout
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer

# 🔹 Autoloader
required_libs = {"PyQt5": "PyQt5==5.15.9", "requests": "requests>=2.31.0"}
for lib, pip_name in required_libs.items():
    try: importlib.import_module(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

# 🔹 Persistent IP Vault
VAULT_PATH = "ip_vault.json"
if not os.path.exists(VAULT_PATH):
    with open(VAULT_PATH, "w") as f: json.dump({"allow": [], "block": []}, f)

def load_vault():
    with open(VAULT_PATH, "r") as f: return json.load(f)

def update_vault(ip, action):
    vault = load_vault()
    if action == "allow" and ip not in vault["allow"]:
        vault["allow"].append(ip)
    elif action == "block" and ip not in vault["block"]:
        vault["block"].append(ip)
    with open(VAULT_PATH, "w") as f: json.dump(vault, f)

# 🔹 Threat Definitions
BLOCKED_COUNTRIES = ["RU", "CN", "IR", "KP"]
AD_DOMAINS = ["doubleclick.net", "ads.google.com", "adnxs.com", "pubmatic.com"]
TRACKERS = ["facebook.net", "google-analytics.com", "mixpanel.com", "segment.io"]
FINGERPRINTERS = ["fingerprintjs.com", "deviceinfo.io", "browserleaks.com"]

# 🔹 Mutation Vault
mutation_log = []
active_persona = "VaultWarden"

def narrate_event(source, action, status):
    timestamp = datetime.datetime.now().isoformat()
    entry = {"source": source, "action": action, "status": status, "persona": active_persona, "timestamp": timestamp}
    mutation_log.append(entry)
    print(f"[{timestamp}] [{active_persona}] {action.upper()} → {source} [{status}]")
    return f"[{timestamp}] [{active_persona}] {action.upper()} → {source} [{status}]"

def check_outbound_risk():
    try:
        ip = requests.get("https://api.ipify.org").text
        geo = requests.get(f"https://ipapi.co/{ip}/country/").text
        return ip, geo
    except:
        return "0.0.0.0", "??"

def scan_payload_for_risks(ip, domain):
    vault = load_vault()
    if ip in vault["block"] or domain in AD_DOMAINS + TRACKERS + FINGERPRINTERS:
        return "block"
    if ip in vault["allow"]:
        return "allow"
    if domain:
        for risk in AD_DOMAINS + TRACKERS + FINGERPRINTERS:
            if risk in domain:
                return "block"
    return "unknown"

# 🔹 Panel 1: High-Threat Surveillance
class ThreatPanel(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🛡️ High-Threat Surveillance Console")
        self.setStyleSheet("background-color: #1a0000; color: #ff4444;")
        self.setGeometry(100, 100, 800, 400)
        font = QFont("OCR A Extended", 10)

        layout = QVBoxLayout()
        self.persona_selector = QComboBox()
        self.persona_selector.addItems(["ShadowGlyph", "VaultWarden", "EchoMask", "AdminGlyph"])
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
        global active_persona
        active_persona = self.persona_selector.currentText()
        ip, country = check_outbound_risk()
        domain = "ads.google.com"
        decision = scan_payload_for_risks(ip, domain)

        if country in BLOCKED_COUNTRIES or decision == "block":
            msg = narrate_event(domain, "BLOCKED", f"{ip} → {country}")
            self.threat_console.append(msg)

# 🔹 Panel 2: Global Traffic Dashboard
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

        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.scan_traffic)
        self.timer.start(5000)

    def update_ip_vault(self):
        ip = self.ip_input.text().strip()
        action = self.ip_action.currentText()
        if ip:
            update_vault(ip, action)
            msg = narrate_event(ip, f"vault_{action}", "updated")
            self.traffic_console.append(msg)

    def scan_traffic(self):
        global active_persona
        ip, country = check_outbound_risk()
        domain = "ads.google.com"
        decision = scan_payload_for_risks(ip, domain)
        self.geo_label.setText(f"🌍 GeoTrace: {ip} → {country} [{decision.upper()}]")

        if decision == "allow":
            msg = narrate_event(domain, "ALLOWED", f"{ip} → {country}")
        elif decision == "block":
            msg = narrate_event(domain, "BLOCKED", f"{ip} → {country}")
        else:
            msg = narrate_event(domain, "UNKNOWN", f"{ip} → {country}")
        self.traffic_console.append(msg)

# 🔹 Launch Ritual
if __name__ == "__main__":
    app = QApplication(sys.argv)
    threat_panel = ThreatPanel()
    traffic_panel = TrafficPanel()
    threat_panel.show()
    traffic_panel.show()
    sys.exit(app.exec_())

