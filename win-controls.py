# 🔧 Autoloader: Ensures all required libraries are installed
import importlib.util
import subprocess
import sys

def autoload_libraries():
    required = ["PySide6", "psutil"]
    for lib in required:
        if importlib.util.find_spec(lib) is None:
            print(f"⚠️ Library '{lib}' not found. Installing...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
        else:
            print(f"🧠 Library '{lib}' is already installed.")

autoload_libraries()

# 🔮 ASI Control Shell Panels
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QListWidget
from PySide6.QtCore import QTimer
import psutil, random

# Core Pulse Panel
class CorePulsePanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.status = QLabel("Initializing Core Pulse...")
        layout.addWidget(self.status)
        self.setLayout(layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_pulse)
        self.timer.start(1000)

    def update_pulse(self):
        cpu = psutil.cpu_percent()
        ram = psutil.virtual_memory().percent
        glyph = "🧠" if cpu < 50 else "⚠️"
        self.status.setText(f"{glyph} CPU: {cpu}% | RAM: {ram}%")

# Threat Matrix Panel
class ThreatMatrixPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.status = QLabel("Scanning for anomalies...")
        layout.addWidget(self.status)
        self.setLayout(layout)
        self.update_matrix()

    def update_matrix(self):
        threat_level = random.choice(["Safe", "Suspicious", "Purge"])
        glyph = {"Safe": "🟢", "Suspicious": "🟡", "Purge": "🔴"}[threat_level]
        self.status.setText(f"{glyph} Threat Level: {threat_level}")

# Settings Dominion Panel
class SettingsDominionPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Choose Display Resolution:")
        self.dropdown = QComboBox()
        self.dropdown.addItems(["1920x1080", "1280x720", "1024x768"])
        self.button = QPushButton("Apply Resolution")
        self.button.clicked.connect(self.apply_resolution)
        layout.addWidget(self.label)
        layout.addWidget(self.dropdown)
        layout.addWidget(self.button)
        self.setLayout(layout)

    def apply_resolution(self):
        res = self.dropdown.currentText()
        cmd = f"powershell.exe Set-DisplayResolution -Width {res.split('x')[0]} -Height {res.split('x')[1]}"
        subprocess.run(cmd, shell=True)
        self.label.setText(f"🧠 Resolution set to {res}")

# Daemon Control Panel
class DaemonControlPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.status = QLabel("🟢 Autoloader: Active")
        self.toggle_button = QPushButton("Stop Autoloader")
        self.ingest_button = QPushButton("Trigger Ingest Daemon")
        self.toggle_button.clicked.connect(self.toggle_autoloader)
        self.ingest_button.clicked.connect(self.trigger_ingest)
        layout.addWidget(self.status)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.ingest_button)
        self.setLayout(layout)
        self.autoloader_active = True

    def toggle_autoloader(self):
        if self.autoloader_active:
            subprocess.run("powershell.exe Stop-Service Autoloader", shell=True)
            self.status.setText("🔴 Autoloader: Halted")
            self.toggle_button.setText("Start Autoloader")
        else:
            subprocess.run("powershell.exe Start-Service Autoloader", shell=True)
            self.status.setText("🟢 Autoloader: Active")
            self.toggle_button.setText("Stop Autoloader")
        self.autoloader_active = not self.autoloader_active

    def trigger_ingest(self):
        subprocess.run("powershell.exe Start-Process ingest_daemon.exe", shell=True)
        self.status.setText("⚙️ Ingest Daemon Triggered")

# Codex Rule Engine Panel
class CodexRuleEnginePanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.status = QLabel("🧬 Rule: Retain purge logs for 72h if threat < 3")
        self.toggle_button = QPushButton("Mutate Rule")
        self.sync_button = QPushButton("Trigger Swarm Sync")
        self.toggle_button.clicked.connect(self.mutate_rule)
        self.sync_button.clicked.connect(self.trigger_sync)
        layout.addWidget(self.status)
        layout.addWidget(self.toggle_button)
        layout.addWidget(self.sync_button)
        self.setLayout(layout)
        self.rule_active = True

    def mutate_rule(self):
        if self.rule_active:
            self.status.setText("🧨 Rule Mutated: Retain logs for 24h if threat < 2")
            self.toggle_button.setText("Restore Rule")
        else:
            self.status.setText("🧬 Rule: Retain purge logs for 72h if threat < 3")
            self.toggle_button.setText("Mutate Rule")
        self.rule_active = not self.rule_active

    def trigger_sync(self):
        subprocess.run("powershell.exe Copy-Item rules.json -Destination \\\\node2\\sync\\rules.json", shell=True)
        self.status.setText("🔁 Sync Triggered: Rules pushed to swarm")

# Country Filter Panel
class CountryFilterPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.label = QLabel("Allowed Countries:")
        self.country_list = QListWidget()
        self.country_list.addItems(["United States", "Germany", "Japan"])
        self.block_button = QPushButton("Block Selected Country")
        self.allow_button = QPushButton("Allow New Country")
        self.block_button.clicked.connect(self.block_country)
        self.allow_button.clicked.connect(self.allow_country)
        layout.addWidget(self.label)
        layout.addWidget(self.country_list)
        layout.addWidget(self.block_button)
        layout.addWidget(self.allow_button)
        self.setLayout(layout)

    def block_country(self):
        selected = self.country_list.currentItem()
        if selected:
            self.label.setText(f"🔴 Blocked: {selected.text()}")

    def allow_country(self):
        self.country_list.addItem("NewCountry")
        self.label.setText("🟢 Allowed: NewCountry")

# Event Bus Panel
class EventBusPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.status = QLabel("📊 Monitoring Windows Events...")
        self.refresh_button = QPushButton("Refresh Logs")
        self.refresh_button.clicked.connect(self.refresh_logs)
        layout.addWidget(self.status)
        layout.addWidget(self.refresh_button)
        self.setLayout(layout)

    def refresh_logs(self):
        logs = subprocess.check_output("powershell.exe Get-WinEvent -LogName System -MaxEvents 5", shell=True)
        self.status.setText(f"🧠 Latest Events:\n{logs.decode('utf-8')[:300]}")

# ASI Persona Status Panel
class PersonaStatusPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        self.status = QLabel("🧠 Agent: Codex Sentinel\nRole: Threat Analyst\nState: Active")
        self.toggle_button = QPushButton("Toggle Agent State")
        self.toggle_button.clicked.connect(self.toggle_state)
        layout.addWidget(self.status)
        layout.addWidget(self.toggle_button)
        self.setLayout(layout)
        self.active = True

    def toggle_state(self):
        self.active = not self.active
        state = "Active" if self.active else "Suspended"
        glyph = "🧠" if self.active else "⛔"
        self.status.setText(f"{glyph} Agent: Codex Sentinel\nRole: Threat Analyst\nState: {state}")

# Unified Shell
class ASIControlShell(QTabWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASI Control Shell")
        self.setFixedSize(700, 600)
        self.addTab(CorePulsePanel(), "Core Pulse")
        self.addTab(ThreatMatrixPanel(), "Threat Matrix")
        self.addTab(SettingsDominionPanel(), "Settings Dominion")
        self.addTab(DaemonControlPanel(), "Daemon Control")
        self.addTab(CodexRuleEnginePanel(), "Codex Rule Engine")
        self.addTab(CountryFilterPanel(), "Country Filter")
        self.addTab(EventBusPanel(), "Event Bus")
        self.addTab(PersonaStatusPanel(), "ASI Persona Status")

app = QApplication([])
window = ASIControlShell()
window.show()
app.exec()

