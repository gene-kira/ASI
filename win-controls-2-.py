import importlib.util, subprocess, sys, psutil, random
from PySide6.QtWidgets import QApplication, QTabWidget, QWidget, QVBoxLayout, QLabel, QPushButton, QComboBox, QListWidget
from PySide6.QtCore import QTimer

# 🔧 Autoloader
for lib in ["PySide6", "psutil"]:
    if importlib.util.find_spec(lib) is None:
        subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

# 🔩 Base Panel
class BasePanel(QWidget):
    def __init__(self, title):
        super().__init__()
        self.setWindowTitle(title)
        self.layout = QVBoxLayout()
        self.setLayout(self.layout)
    def add(self, *widgets):
        for w in widgets: self.layout.addWidget(w)

# 🧠 Core Pulse
class CorePulse(BasePanel):
    def __init__(self):
        super().__init__("Core Pulse")
        self.status = QLabel("Initializing...")
        self.add(self.status)
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update)
        self.timer.start(1000)
    def update(self):
        cpu, ram = psutil.cpu_percent(), psutil.virtual_memory().percent
        self.status.setText(f"[OK] CPU:{cpu}% RAM:{ram}%")

# 🛡️ Threat Matrix
class ThreatMatrix(BasePanel):
    def __init__(self):
        super().__init__("Threat Matrix")
        level = random.choice(["SAFE", "SUSPICIOUS", "PURGE"])
        self.status = QLabel(f"[{level}] Threat Level")
        self.add(self.status)

# ⚙️ Settings Dominion
class SettingsDominion(BasePanel):
    def __init__(self):
        super().__init__("Settings")
        self.label = QLabel("Choose Resolution:")
        self.dropdown = QComboBox()
        self.dropdown.addItems(["1920x1080", "1280x720", "1024x768"])
        self.button = QPushButton("Apply")
        self.button.clicked.connect(self.apply)
        self.add(self.label, self.dropdown, self.button)
    def apply(self):
        w, h = self.dropdown.currentText().split("x")
        subprocess.run(f"powershell.exe Set-DisplayResolution -Width {w} -Height {h}", shell=True)
        self.label.setText(f"[OK] Resolution set to {w}x{h}")

# 🔄 Daemon Control
class DaemonControl(BasePanel):
    def __init__(self):
        super().__init__("Daemon Control")
        self.status = QLabel("[ACTIVE] Autoloader")
        self.toggle = QPushButton("Stop")
        self.trigger = QPushButton("Trigger Ingest")
        self.toggle.clicked.connect(self.flip)
        self.trigger.clicked.connect(self.ingest)
        self.add(self.status, self.toggle, self.trigger)
        self.active = True
    def flip(self):
        cmd = "Stop" if self.active else "Start"
        subprocess.run(f"powershell.exe {cmd}-Service Autoloader", shell=True)
        self.status.setText(f"[{'HALTED' if self.active else 'ACTIVE'}] Autoloader")
        self.toggle.setText("Start" if self.active else "Stop")
        self.active = not self.active
    def ingest(self):
        subprocess.run("powershell.exe Start-Process ingest_daemon.exe", shell=True)
        self.status.setText("[TRIGGERED] Ingest Daemon")

# 📜 Codex Rule Engine
class CodexRuleEngine(BasePanel):
    def __init__(self):
        super().__init__("Codex Rule Engine")
        self.status = QLabel("[OK] Rule: Retain logs 72h")
        self.mutate = QPushButton("Mutate Rule")
        self.sync = QPushButton("Trigger Sync")
        self.mutate.clicked.connect(self.flip)
        self.sync.clicked.connect(self.sync_rules)
        self.add(self.status, self.mutate, self.sync)
        self.active = True
    def flip(self):
        self.active = not self.active
        self.status.setText("[MUTATED] Retain logs 24h" if not self.active else "[OK] Retain logs 72h")
        self.mutate.setText("Restore" if not self.active else "Mutate")
    def sync_rules(self):
        subprocess.run("powershell.exe Copy-Item rules.json -Destination \\\\node2\\sync\\rules.json", shell=True)
        self.status.setText("[OK] Sync Triggered")

# 🌐 Country Filter
class CountryFilter(BasePanel):
    def __init__(self):
        super().__init__("Country Filter")
        self.label = QLabel("Allowed Countries:")
        self.list = QListWidget()
        self.list.addItems(["United States", "Germany", "Japan"])
        self.block = QPushButton("Block Selected")
        self.allow = QPushButton("Allow New")
        self.block.clicked.connect(self.block_country)
        self.allow.clicked.connect(self.allow_country)
        self.add(self.label, self.list, self.block, self.allow)
    def block_country(self):
        item = self.list.currentItem()
        if item: self.label.setText(f"[BLOCKED] {item.text()}")
    def allow_country(self):
        self.list.addItem("NewCountry")
        self.label.setText("[ALLOWED] NewCountry")

# 📊 Event Bus
class EventBus(BasePanel):
    def __init__(self):
        super().__init__("Event Bus")
        self.status = QLabel("[EVENT] Monitoring...")
        self.refresh = QPushButton("Refresh Logs")
        self.refresh.clicked.connect(self.update)
        self.add(self.status, self.refresh)
    def update(self):
        logs = subprocess.check_output("powershell.exe Get-WinEvent -LogName System -MaxEvents 5", shell=True)
        self.status.setText(f"[OK] Events:\n{logs.decode('utf-8')[:300]}")

# 🧠 ASI Persona Status
class PersonaStatus(BasePanel):
    def __init__(self):
        super().__init__("ASI Persona Status")
        self.status = QLabel("[ACTIVE] Codex Sentinel")
        self.toggle = QPushButton("Toggle State")
        self.toggle.clicked.connect(self.flip)
        self.add(self.status, self.toggle)
        self.active = True
    def flip(self):
        self.active = not self.active
        state = "ACTIVE" if self.active else "SUSPENDED"
        self.status.setText(f"[{state}] Codex Sentinel")

# 🧬 Registry Mutation
class RegistryMutation(BasePanel):
    def __init__(self):
        super().__init__("Registry Mutation")
        self.status = QLabel("[OK] Registry Ready")
        self.hive = QComboBox()
        self.hive.addItems(["HKLM", "HKCU", "HKCR", "HKU", "HKCC"])
        self.mutate = QPushButton("Mutate Key")
        self.delete = QPushButton("Delete Key")
        self.mutate.clicked.connect(self.mutate_key)
        self.delete.clicked.connect(self.delete_key)
        self.add(self.status, self.hive, self.mutate, self.delete)
    def mutate_key(self):
        h = self.hive.currentText()
        subprocess.run(f'reg add "{h}\\Software\\ASI\\Codex" /v PurgeRetention /t REG_SZ /d "72h" /f', shell=True)
        self.status.setText("[MUTATED] Key Added")
    def delete_key(self):
        h = self.hive.currentText()
        subprocess.run(f'reg delete "{h}\\Software\\ASI\\Codex" /v PurgeRetention /f', shell=True)
        self.status.setText("[DELETED] Key Removed")

# 🧩 Unified Shell
app = QApplication([])
shell = QTabWidget()
shell.setWindowTitle("ASI Control Shell")
shell.setFixedSize(700, 600)
for panel in [CorePulse(), ThreatMatrix(), SettingsDominion(), DaemonControl(), CodexRuleEngine(),
              CountryFilter(), EventBus(), PersonaStatus(), RegistryMutation()]:
    shell.addTab(panel, panel.windowTitle())
shell.show()
app.exec()

