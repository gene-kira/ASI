import ctypes, sys, threading, time, subprocess, importlib, socket, hmac, hashlib, json, os
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QComboBox, QLabel, QTableWidget, QTableWidgetItem, QTextEdit
from PyQt6.QtCore import QTimer

# === Elevation Check ===
def ensure_admin():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()
ensure_admin()

# === Autoloader ===
for lib in ["ip2location"]:
    try: importlib.import_module(lib)
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# === Country Mapping ===
COUNTRIES = {
    "United States": "US", "Germany": "DE", "China": "CN", "Brazil": "BR", "Canada": "CA",
    "United Kingdom": "GB", "France": "FR", "Japan": "JP", "India": "IN", "Australia": "AU"
}

# === Config Loader ===
def load_json(path): return json.load(open(path)) if os.path.exists(path) else {}
def save_json(path, data): json.dump(data, open(path, "w"), indent=2)

# === Core Classes ===
class Registry:
    def __init__(self, key): self.key = key; self.data = {}
    def sign(self, *args): return hmac.new(self.key, "|".join(args).encode(), hashlib.sha256).hexdigest()
    def register(self, id, *args): self.data[id] = {"data": args, "sig": self.sign(id, *args)}
    def verify(self, id, sig): return hmac.compare_digest(sig, self.data.get(id, {}).get("sig", ""))

class Override:
    def __init__(self): self.allowed = set(load_json("manual_overrides.json"))
    def allow(self, key): self.allowed.add(key); save_json("manual_overrides.json", list(self.allowed))
    def is_allowed(self, key): return key in self.allowed

class CountryFilter:
    def __init__(self): self.allowed = set(load_json("allowed_countries.json") or ["US", "CA", "GB"])
    def is_allowed(self, code): return code in self.allowed
    def toggle(self, code):
        if code in self.allowed: self.allowed.remove(code)
        else: self.allowed.add(code)
        save_json("allowed_countries.json", list(self.allowed))

class Enforcer:
    def __init__(self, codex, override, registry, country_filter):
        self.codex, self.override, self.registry, self.country_filter = codex, override, registry, country_filter
        try:
            self.geo = importlib.import_module("ip2location").IP2Location("IP2LOCATION-LITE-DB1.BIN")
        except:
            self.geo = None
        self.log = []
    def start(self): threading.Thread(target=self.monitor, daemon=True).start()
    def monitor(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("0.0.0.0", 9999))
        while True:
            try:
                data, addr = sock.recvfrom(1024)
                src, dst, port = addr[0], "unknown", str(addr[1])
                country = self.geo.get_country_short(src) if self.geo else "??"
                tag = f"TAG-1234-5678-{self.registry.sign('1234-5678')}"
                key = f"{src}->{dst}:{port}"
                status = "🟢 Verified" if self.registry.verify("1234-5678", tag.split("-")[2]) else "🔴 Spoofed"
                if not self.country_filter.is_allowed(country): status = "🟡 Blocked"
                if not self.override.is_allowed(key) and key not in self.codex: status = "🔴 Quarantined"
                self.log.append({"src": src, "dst": dst, "port": port, "status": status, "country": country})
            except Exception as e:
                print(f"[Monitor Error] {e}")
                time.sleep(0.1)

# === PyQt6 GUI ===
class NexusConsole(QWidget):
    def __init__(self, enforcer, override, country_filter):
        super().__init__()
        self.enforcer, self.override, self.country_filter = enforcer, override, country_filter
        self.setWindowTitle("Codex Sentinel — Nexus Console")
        self.setStyleSheet("background-color: #121417; color: #00eaff;")
        layout = QVBoxLayout()

        self.table = QTableWidget(0, 5)
        self.table.setHorizontalHeaderLabels(["Source", "Destination", "Port", "Status", "Country"])
        self.table.setStyleSheet("background-color: #1a1c2c; color: #00eaff;")
        layout.addWidget(self.table)

        controls = QHBoxLayout()
        self.allow_btn = QPushButton("Allow"); self.allow_btn.clicked.connect(self.allow_selected)
        self.disallow_btn = QPushButton("Disallow"); self.disallow_btn.clicked.connect(self.disallow_selected)
        self.refresh_btn = QPushButton("Refresh"); self.refresh_btn.clicked.connect(self.refresh)
        self.country_picker = QComboBox(); self.country_picker.addItems(sorted(COUNTRIES.keys()))
        self.toggle_btn = QPushButton("Toggle Country"); self.toggle_btn.clicked.connect(self.toggle_country)
        for btn in [self.allow_btn, self.disallow_btn, self.refresh_btn, self.toggle_btn]:
            btn.setStyleSheet("background-color: #2c2f3a; color: #00eaff; font-weight: bold;")
        controls.addWidget(self.allow_btn)
        controls.addWidget(self.disallow_btn)
        controls.addWidget(self.refresh_btn)
        controls.addWidget(self.country_picker)
        controls.addWidget(self.toggle_btn)
        layout.addLayout(controls)

        self.console = QTextEdit(); self.console.setReadOnly(True)
        self.console.setStyleSheet("background-color: #0f111a; color: #00eaff;")
        layout.addWidget(self.console)

        self.setLayout(layout)
        self.timer = QTimer(); self.timer.timeout.connect(self.refresh); self.timer.start(3000)

    def refresh(self):
        self.table.setRowCount(0)
        for e in self.enforcer.log[-50:]:
            row = self.table.rowCount(); self.table.insertRow(row)
            for i, key in enumerate(["src", "dst", "port", "status", "country"]):
                self.table.setItem(row, i, QTableWidgetItem(str(e[key])))

    def allow_selected(self):
        for i in self.table.selectionModel().selectedRows():
            src = self.table.item(i.row(), 0).text()
            dst = self.table.item(i.row(), 1).text()
            port = self.table.item(i.row(), 2).text()
            key = f"{src}->{dst}:{port}"
            self.override.allow(key)
            self.console.append(f"[Override] Allowed: {key}")

    def disallow_selected(self):
        for i in self.table.selectionModel().selectedRows():
            src = self.table.item(i.row(), 0).text()
            dst = self.table.item(i.row(), 1).text()
            port = self.table.item(i.row(), 2).text()
            key = f"{src}->{dst}:{port}"
            self.console.append(f"[Override] Disallowed: {key}")

    def toggle_country(self):
        name = self.country_picker.currentText()
        code = COUNTRIES.get(name)
        if code:
            self.country_filter.toggle(code)
            status = "Allowed" if self.country_filter.is_allowed(code) else "Blocked"
            self.console.append(f"[Country Filter] {name} ({code}) now {status}")

# === Launcher ===
def launch():
    secret = b"ASI-ritual-key"
    codex, override = {}, Override()
    registry = Registry(secret); registry.register("1234-5678", "Sam", "Operator")
    country_filter = CountryFilter()
    enforcer = Enforcer(codex, override, registry, country_filter); enforcer.start()
    app = QApplication(sys.argv)
    console = NexusConsole(enforcer, override, country_filter)
    console.resize(900, 600); console.show()
    sys.exit(app.exec())

if __name__ == "__main__": launch()

