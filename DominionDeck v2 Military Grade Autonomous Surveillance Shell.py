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

# 🔹 Mutation Vault
mutation_log = []
active_persona = "VaultWarden"
BLOCKED_COUNTRIES = ["RU", "CN", "IR", "KP"]
AD_DOMAINS = ["doubleclick.net", "ads.google.com", "adnxs.com", "pubmatic.com"]
TRACKERS = ["facebook.net", "google-analytics.com", "mixpanel.com", "segment.io"]
FINGERPRINTERS = ["fingerprintjs.com", "deviceinfo.io", "browserleaks.com"]

def narrate_event(source, action, status):
    timestamp = datetime.datetime.now().isoformat()
    entry = {"source": source, "action": action, "status": status, "persona": active_persona, "timestamp": timestamp}
    mutation_log.append(entry)
    print(f"[{timestamp}] [{active_persona}] {action.upper()} → {source} [{status}]")

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

# 🔹 GUI Shell
class DominionDeck(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DominionDeck v2 — Autonomous Tactical Shell")
        self.setStyleSheet("background-color: #0a0a0a; color: #00ffcc;")
        self.setGeometry(100, 100, 900, 700)
        font = QFont("OCR A Extended", 10)

        layout = QVBoxLayout()

        # Persona Selector
        self.persona_selector = QComboBox()
        self.persona_selector.addItems(["ShadowGlyph", "VaultWarden", "EchoMask", "AdminGlyph"])
        self.persona_selector.setFont(font)
        layout.addWidget(QLabel("🧬 Persona Overlay"))
        layout.addWidget(self.persona_selector)

        # IP Control Panel
        ip_layout = QHBoxLayout()
        self.ip_input = QLineEdit()
        self.ip_input.setPlaceholderText("Enter IP")
        self.ip_input.setFont(font)
        self.ip_action = QComboBox()
        self.ip_action.addItems(["allow", "block"])
        self.ip_action.setFont(font)
        self.ip_btn = QPushButton("Update Vault")
        self.ip_btn.setFont(font)
        self.ip_btn.clicked.connect(self.update_ip_vault)
        ip_layout.addWidget(self.ip_input)
        ip_layout.addWidget(self.ip_action)
        ip_layout.addWidget(self.ip_btn)
        layout.addWidget(QLabel("🔐 IP Vault Control"))
        layout.addLayout(ip_layout)

        # Mutation Stream Console
        self.console = QTextEdit()
        self.console.setFont(font)
        self.console.setReadOnly(True)
        layout.addWidget(QLabel("📡 Mutation Stream Console"))
        layout.addWidget(self.console)

        # GeoTrace Dashboard
        self.geo_label = QLabel("🌍 GeoTrace: [Initializing...]")
        self.geo_label.setFont(font)
        layout.addWidget(self.geo_label)

        self.setLayout(layout)

        # Autonomous loop
        self.timer = QTimer()
        self.timer.timeout.connect(self.autonomous_cycle)
        self.timer.start(5000)

    def update_ip_vault(self):
        ip = self.ip_input.text().strip()
        action = self.ip_action.currentText()
        if ip:
            update_vault(ip, action)
            self.console.append(f"🔧 IP {ip} added to {action.upper()} list")
            narrate_event(ip, f"vault_{action}", "updated")

    def autonomous_cycle(self):
        global active_persona
        active_persona = self.persona_selector.currentText()
        ip, country = check_outbound_risk()
        domain = "ads.google.com"  # Simulated outbound domain
        decision = scan_payload_for_risks(ip, domain)

        timestamp = datetime.datetime.now().isoformat()
        self.geo_label.setText(f"🌍 GeoTrace: {ip} → {country} [{decision.upper()}]")

        if country in BLOCKED_COUNTRIES or decision == "block":
            self.console.append(f"[{timestamp}] 🚨 Blocked outbound to {country} / {domain}")
            narrate_event(domain, "lockdown", f"to {country}")
        elif decision == "allow":
            self.console.append(f"[{timestamp}] ✅ Allowed outbound to {country} / {domain}")
            narrate_event(domain, "allowed", f"to {country}")
        else:
            self.console.append(f"[{timestamp}] ⚠️ Unknown outbound to {country} / {domain}")
            narrate_event(domain, "unknown", f"to {country}")

# 🔹 Launch Ritual
if __name__ == "__main__":
    app = QApplication(sys.argv)
    deck = DominionDeck()
    deck.show()
    sys.exit(app.exec_())

