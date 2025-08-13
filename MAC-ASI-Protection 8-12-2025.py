import sys
import os
import subprocess
import random
import time
import ctypes
import json
import threading
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QLineEdit
from PyQt5.QtCore import Qt

# 🧬 Constants
GUI_ENABLED = True
VAULT_PATH = os.path.expanduser("~/.mythic_mac_vault.json")

# 🛡️ Admin Elevation
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    if not is_admin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

# 🔐 Vault Logging
def log_to_vault(symbol, mac):
    entry = {
        "symbol": symbol,
        "mac": mac,
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S")
    }
    try:
        if os.path.exists(VAULT_PATH):
            with open(VAULT_PATH, "r") as f:
                data = json.load(f)
        else:
            data = []
        data.append(entry)
        with open(VAULT_PATH, "w") as f:
            json.dump(data, f, indent=2)
    except Exception as e:
        print(f"Vault logging failed: {e}")

# 🧪 MAC Reader
def get_real_mac():
    try:
        output = subprocess.check_output("getmac", shell=True).decode()
        for line in output.splitlines():
            if "-" in line:
                return line.split()[0].replace("-", "")
    except Exception:
        pass
    return "Unknown"

# 🎭 Mythic MAC Generator
def generate_mythic_mac(symbol):
    prefix = "00E0FC"
    suffix = "".join(random.choices("0123456789ABCDEF", k=6))
    return (prefix + suffix).upper()

# 🧰 MAC Spoofer
def spoof_mac_windows(symbol="phoenix", manual_mac=None):
    elevate()
    adapter_key = r"HKEY_LOCAL_MACHINE\SYSTEM\CurrentControlSet\Control\Class\{4d36e972-e325-11ce-bfc1-08002be10318}\0001"
    mac = manual_mac if manual_mac else generate_mythic_mac(symbol)
    try:
        subprocess.run(["reg", "add", adapter_key, "/v", "NetworkAddress", "/d", mac, "/f"], check=True)
        subprocess.run(["wmic", "nic", "where", "NetEnabled=true", "call", "disable"], check=True)
        time.sleep(1)
        subprocess.run(["wmic", "nic", "where", "NetEnabled=false", "call", "enable"], check=True)
        log_to_vault(symbol, mac)
    except Exception as e:
        print(f"MAC spoofing failed: {e}")

# 🧿 Rogue Detection + Mutation
def scan_for_rogues():
    # Simulated rogue detection (replace with real logic)
    return random.choice([True, False, False, False])  # ~25% chance

def auto_mutate_mac(symbol="phoenix"):
    mac = generate_mythic_mac(symbol)
    spoof_mac_windows(symbol=symbol, manual_mac=mac)
    print(f"⚠️ Rogue detected! Mutated MAC to {mac}")
    log_to_vault(symbol, mac)
    return mac

def rogue_defense_loop(symbol="phoenix", interval=10):
    print("🛡️ Starting real-time rogue defense...")
    while True:
        if scan_for_rogues():
            auto_mutate_mac(symbol)
        time.sleep(interval)

# 🧙 Mythic GUI
class MythicGUI(QWidget):
    def __init__(self, symbol="phoenix"):
        super().__init__()
        self.symbol = symbol
        self.real_mac = get_real_mac()
        self.spoofed_mac = None
        self.defense_active = False
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("🧬 Mythic MAC Spoofer")
        self.setGeometry(100, 100, 400, 250)

        self.label = QLabel(self.get_label_text(), self)
        self.label.setAlignment(Qt.AlignCenter)

        self.manual_input = QLineEdit(self)
        self.manual_input.setPlaceholderText("Enter 12-digit MAC (e.g. 00E0FC123456)")

        self.manual_button = QPushButton("Spoof Manual MAC", self)
        self.manual_button.clicked.connect(self.spoof_manual)

        self.mythic_button = QPushButton("Generate Mythic MAC", self)
        self.mythic_button.clicked.connect(self.spoof_mythic)

        self.defense_button = QPushButton("Activate Rogue Defense", self)
        self.defense_button.clicked.connect(self.toggle_defense)

        layout = QVBoxLayout()
        layout.addWidget(self.label)
        layout.addWidget(self.manual_input)
        layout.addWidget(self.manual_button)
        layout.addWidget(self.mythic_button)
        layout.addWidget(self.defense_button)
        self.setLayout(layout)

    def get_label_text(self):
        return f"🧠 Symbol: {self.symbol}\n🔍 Real MAC: {self.real_mac}\n🎭 Spoofed MAC: {self.spoofed_mac or 'None'}"

    def update_label(self):
        self.label.setText(self.get_label_text())

    def spoof_manual(self):
        mac = self.manual_input.text().strip().upper()
        if len(mac) == 12 and all(c in "0123456789ABCDEF" for c in mac):
            spoof_mac_windows(symbol=self.symbol, manual_mac=mac)
            self.spoofed_mac = mac
            self.real_mac = get_real_mac()
            self.update_label()
        else:
            self.label.setText("❌ Invalid MAC format. Use 12 hex characters.")

    def spoof_mythic(self):
        mac = generate_mythic_mac(self.symbol)
        spoof_mac_windows(symbol=self.symbol, manual_mac=mac)
        self.spoofed_mac = mac
        self.real_mac = get_real_mac()
        self.update_label()

    def toggle_defense(self):
        if not self.defense_active:
            self.defense_active = True
            self.defense_button.setText("🛡️ Rogue Defense Active")
            threading.Thread(target=rogue_defense_loop, args=(self.symbol,), daemon=True).start()
        else:
            self.label.setText("⚠️ Defense already running.")

# 🚀 Launch GUI
def show_mutation_console(symbol="phoenix"):
    app = QApplication(sys.argv)
    gui = MythicGUI(symbol=symbol)
    gui.show()
    sys.exit(app.exec_())

# 🧿 Entry Point
if __name__ == "__main__":
    manual_mac = None
    for arg in sys.argv:
        if arg.startswith("--mac="):
            manual_mac = arg.split("=")[1]

    if "--rogue" in sys.argv:
        rogue_defense_loop(symbol="phoenix", interval=10)
    elif GUI_ENABLED:
        show_mutation_console("phoenix")
    else:
        spoof_mac_windows(symbol="phoenix", manual_mac=manual_mac)

