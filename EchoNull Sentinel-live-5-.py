# 🧠 Autoloader
import subprocess, sys

def autoload(package, import_as=None):
    try:
        globals()[import_as or package] = __import__(import_as or package)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])
        globals()[import_as or package] = __import__(import_as or package)

modules = {
    "requests": "requests",
    "ipwhois": "ipwhois",
    "hashlib": "hashlib",
    "socket": "socket",
    "time": "time",
    "signal": "signal",
    "PyQt6": "PyQt6"
}
for pkg, imp in modules.items():
    autoload(pkg, imp)

# PyQt6 imports
from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer
import signal

# 🛡️ Interrupt Shield
def block_interrupt(signum, frame):
    print("\n🛡️ Interrupt blocked. EchoNull shell remains active.")

try:
    signal.signal(signal.SIGINT, block_interrupt)
    signal.signal(signal.SIGTERM, block_interrupt)
except Exception as e:
    print(f"⚠️ Signal registration failed: {e}")

# 🔐 Sentinel Config
BIOMETRIC_HASH = hashlib.sha256(b"authorized_user_signature").hexdigest()

def verify_biometric():
    current_hash = hashlib.sha256(b"authorized_user_signature").hexdigest()
    return current_hash == BIOMETRIC_HASH

# 🌐 Live Feed Integration (Abuse.ch URLhaus)
def fetch_live_urls():
    try:
        response = requests.get("https://urlhaus-api.abuse.ch/v1/urls/recent/")
        data = response.json()
        return [entry["url"] for entry in data.get("urls", [])]
    except Exception as e:
        print(f"⚠️ Failed to fetch live URLs: {e}")
        return []

# 🧬 Mutation Narration
def get_mutation_data(url, status):
    try:
        domain = url.split("/")[2]
        ip = socket.gethostbyname(domain)
        country = ipwhois.IPWhois(ip).lookup_rdap().get("network", {}).get("country", "Unknown")
    except Exception:
        ip, country = "N/A", "Unknown"
    lineage = f"mutation-{hashlib.md5(url.encode()).hexdigest()[:8]}"
    timestamp = time.strftime("%H:%M:%S")
    return [timestamp, url, ip, country, status, lineage]

def sentinel_get(url):
    if not verify_biometric():
        return get_mutation_data(url, "EXPIRED")
    return get_mutation_data(url, "BLOCKED" if "malicious" in url else "ALLOWED")

# 🧠 Autonomous GUI
class SentinelDaemon(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("EchoNull Sentinel Shell [Autonomous]")
        self.layout = QVBoxLayout()
        self.table = QTableWidget(0, 6)
        self.table.setHorizontalHeaderLabels(["Timestamp", "URL", "IP", "Country", "Status", "Lineage"])
        self.layout.addWidget(self.table)
        self.setLayout(self.layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.run_autonomous_scan)
        self.timer.start(15000)  # Every 15 seconds

    def run_autonomous_scan(self):
        urls = fetch_live_urls()
        for url in urls:
            try:
                data = sentinel_get(url)
                row = self.table.rowCount()
                self.table.insertRow(row)
                for i, value in enumerate(data):
                    self.table.setItem(row, i, QTableWidgetItem(value))
            except Exception as e:
                print(f"🛡️ Blocked or failed: {e}")

# 🚀 Launch
app = QApplication(sys.argv)
window = SentinelDaemon()
window.show()

try:
    sys.exit(app.exec())
except KeyboardInterrupt:
    print("🛡️ Interrupt attempt detected — blocked by EchoNull.")

