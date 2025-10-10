import sys, os, ctypes, subprocess, json, time, psutil
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QLabel, QTextEdit, QLineEdit

BLOCKLIST_FILE = "blocklist.py"
LOG_FILE = "mutation_log.json"
MEMORY_FILE = "glyph_memory.json"

# 🔐 Elevation
def is_admin():
    try: return ctypes.windll.shell32.IsUserAnAdmin()
    except: return False

def elevate():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])  # ✅ FIXED bracket
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)

if not is_admin():
    elevate()
    sys.exit()

# 🧠 Mutation Logger
def log_mutation(action, target):
    entry = {"action": action, "target": target, "timestamp": time.time()}
    with open(LOG_FILE, "a") as f:
        f.write(json.dumps(entry) + "\n")

# 🧬 Memory Engine
def remember_glyph(ip, ritual):
    memory = {}
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r") as f:
            memory = json.load(f)
    memory[ip] = ritual
    with open(MEMORY_FILE, "w") as f:
        json.dump(memory, f, indent=2)

# 🛡️ Block IP
def block_ip(ip):
    subprocess.call(["netsh", "advfirewall", "firewall", "add", "rule",
                     f"name=AutoBlock_{ip}", "dir=out", "action=block", f"remoteip={ip}"])
    log_mutation("block", ip)
    remember_glyph(ip, "block")

# 🧹 Uninstall App
def uninstall_app(app_name):
    cmd = f'wmic product where "name like \'%{app_name}%\'" call uninstall'
    subprocess.call(cmd, shell=True)
    log_mutation("uninstall", app_name)

# 🔍 Scan Connections
def scan_glyphs():
    glyphs = []
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'ESTABLISHED' and conn.raddr:
            ip = conn.raddr.ip
            ritual = "Block" if ip.startswith("13.") or ip.startswith("20.") or "ads" in ip or "telemetry" in ip else "Observe"
            glyphs.append(f"{ip}: {ritual}")
    return "\n".join(glyphs)

# 🔦 Reveal Hidden Rituals
def reveal_hidden():
    output = ""
    try:
        tasks = subprocess.check_output("schtasks", shell=True).decode(errors='ignore')
        hidden_tasks = [line for line in tasks.splitlines() if any(tag in line.lower() for tag in ["telemetry", "customer", "ceip", "update"])]
        output += "Hidden Tasks:\n" + "\n".join(hidden_tasks) + "\n"
    except: output += "Task scan failed\n"

    try:
        services = subprocess.check_output("sc query", shell=True).decode(errors='ignore')
        hidden_services = [line for line in services.splitlines() if any(tag in line.lower() for tag in ["telemetry", "update", "tracking", "feedback"])]
        output += "Hidden Services:\n" + "\n".join(hidden_services) + "\n"
    except: output += "Service scan failed\n"

    try:
        logs = subprocess.check_output('wevtutil qe System /f:text /c:10 /q:"*[System[(Level=2)]]"', shell=True).decode(errors='ignore')
        output += "Recent Errors:\n" + logs
    except: output += "Event log access failed\n"

    return output

# 🧿 GUI Overlay
class WinSpy(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setWindowTitle('WinSpy Symbolic Control Shell')
        self.setGeometry(100, 100, 900, 600)

        self.label = QLabel('Enter IP or App Name:', self)
        self.label.move(20, 20)

        self.input = QLineEdit(self)
        self.input.setGeometry(180, 20, 680, 25)

        self.output = QTextEdit(self)
        self.output.setGeometry(20, 60, 860, 420)

        self.scan_btn = QPushButton('🔍 Scan Glyphs', self)
        self.scan_btn.setGeometry(20, 500, 120, 30)
        self.scan_btn.clicked.connect(self.scan_glyphs)

        self.block_btn = QPushButton('🛡️ Block Ritual', self)
        self.block_btn.setGeometry(160, 500, 120, 30)
        self.block_btn.clicked.connect(self.block_ritual)

        self.uninstall_btn = QPushButton('🧹 Purge App', self)
        self.uninstall_btn.setGeometry(300, 500, 120, 30)
        self.uninstall_btn.clicked.connect(self.purge_app)

        self.reveal_btn = QPushButton('🔦 Reveal Hidden Rituals', self)
        self.reveal_btn.setGeometry(440, 500, 180, 30)
        self.reveal_btn.clicked.connect(self.reveal_rituals)

        self.refresh_btn = QPushButton('📜 Show Recent Mutations', self)
        self.refresh_btn.setGeometry(640, 500, 180, 30)
        self.refresh_btn.clicked.connect(self.show_mutations)

    def scan_glyphs(self):
        self.output.setText(scan_glyphs())

    def block_ritual(self):
        ip = self.input.text()
        block_ip(ip)
        self.output.setText(f"Ritual Invoked: Block {ip}")

    def purge_app(self):
        app = self.input.text()
        uninstall_app(app)
        self.output.setText(f"Ritual Invoked: Uninstall {app}")

    def reveal_rituals(self):
        self.output.setText(reveal_hidden())

    def show_mutations(self):
        if os.path.exists(LOG_FILE):
            with open(LOG_FILE, "r") as f:
                lines = f.readlines()[-10:]
                self.output.setText("📜 Recent Mutations:\n" + "\n".join(lines))
        else:
            self.output.setText("No mutations logged yet.")

# 🚀 Launch GUI
if __name__ == '__main__':
    app = QApplication(sys.argv)
    winspy = WinSpy()
    winspy.show()
    sys.exit(app.exec_())

