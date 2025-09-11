import os, sys, ctypes, socket, hashlib, random, threading
from datetime import datetime
from PyQt5 import QtWidgets, QtCore

# === SELF-ELEVATION ===
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

if not is_admin():
    script = os.path.abspath(sys.argv[0])
    params = ' '.join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit()

# === CONFIG ===
NODE_ID = f"BORG-{random.randint(1000,9999)}"
PERSONAS = ["Watcher", "Sentinel", "Echo", "Fracture", "Oracle", "ThreatHunter", "Compliance Auditor"]
CODENAME = "BorgGuard v11.0 DominionZero"
TRUSTED_ENTITIES = {"BORG-CORE", "QueenNode", "ReplicatorGrid", "PortGuardFrigate"}
PERSONAL_TAGS = ["face", "finger", "bio", "phone", "address", "license", "ssn"]

# === GLOBALS ===
gui_ready = threading.Event()
gui = None

# === DEFENSE CORE ===
class DefenseCore:
    def __init__(self):
        self.codex = {
            "retention": {"Telemetry": 60, "Personal": 86400, "Backdoor": 3, "MAC/IP": 30, "FakeTelemetry": 30},
            "threats": []
        }
        self.threat_db = {}
        self.outbound_db = []

    def ingest(self, packet_id, payload, threat_type):
        timestamp = datetime.utcnow()
        self.threat_db[packet_id] = {"type": threat_type, "payload": payload, "timestamp": timestamp}
        self.narrate("ingest", f"{packet_id} as {threat_type}")
        self.purge_expired()

    def dispatch(self, data_type, payload):
        expiry = self.codex["retention"].get(data_type, 60)
        self.outbound_db.append({
            "type": data_type,
            "payload": payload,
            "timestamp": datetime.utcnow(),
            "expiry": expiry
        })
        self.narrate("dispatch", f"{data_type} dispatched, will self-destruct in {expiry}s")

    def purge_expired(self):
        now = datetime.utcnow()
        for pid in list(self.threat_db.keys()):
            t_type = self.threat_db[pid]["type"]
            age = (now - self.threat_db[pid]["timestamp"]).total_seconds()
            if age > self.codex["retention"].get(t_type, 60):
                del self.threat_db[pid]
                self.narrate("purge", f"{pid} ({t_type}) purged")

        self.outbound_db = [
            entry for entry in self.outbound_db
            if (now - entry["timestamp"]).total_seconds() < entry["expiry"]
        ]

    def mutate_codex(self, ghost_sync=False):
        if ghost_sync:
            self.codex["retention"]["Telemetry"] = max(30, self.codex["retention"]["Telemetry"] - 15)
            if "phantom_node" not in self.codex["threats"]:
                self.codex["threats"].append("phantom_node")
            self.narrate("mutation", "GhostSync detected—codex mutated")

    def narrate(self, event_type, details):
        stories = {
            "ingest": f"📥 The node absorbed: {details}",
            "purge": f"🔥 Memory purged: {details}",
            "mutation": f"🧬 Codex rewritten: {details}",
            "dispatch": f"🚀 Data outbound: {details}"
        }
        print(stories.get(event_type, f"⚙️ System event: {details}"))

def detect_ghost_sync(payload):
    return b"ghost" in payload.lower()

def is_personal_data(payload):
    decoded = payload.decode(errors="ignore").lower()
    return any(tag in decoded for tag in PERSONAL_TAGS)

def is_trusted(entity_id):
    return entity_id in TRUSTED_ENTITIES

def detect_synthetic_agent(metadata):
    tags = metadata.get("agent_tags", [])
    return "ai" in tags or "asi" in tags or "synthetic" in tags

def reject_synthetic_access(metadata):
    if detect_synthetic_agent(metadata):
        print("🚫 Synthetic agent blocked by zero-trust logic.")
        return False
    return True

def generate_fake_telemetry():
    return {
        "cpu": random.randint(1, 100),
        "mem": random.randint(100, 8000),
        "temp": round(random.uniform(30.0, 90.0), 2),
        "node": random.choice(PERSONAS)
    }

# === ENCRYPTED ANCESTRY ===
def generate_ancestry(payload):
    lineage = f"{NODE_ID}-{payload}-{datetime.utcnow().isoformat()}"
    return hashlib.sha256(lineage.encode()).hexdigest()

# === PERSONA ROTATION ===
def rotate_persona():
    return random.choice(PERSONAS)

# === THREAT CLASSIFICATION ===
def classify_threat(payload):
    entropy = sum(payload) % 100
    if entropy > 85: return "Backdoor"
    elif entropy > 65: return "Personal"
    elif entropy > 45: return "MAC/IP"
    else: return "Telemetry"

# === SYMBOLIC FEEDBACK ===
def symbolic_feedback(threat_type):
    return {
        "Telemetry": "📡",
        "Personal": "🧬",
        "Backdoor": "🕳️",
        "MAC/IP": "🔗",
        "FakeTelemetry": "🌀"
    }.get(threat_type, "⚫")

# === GUI OVERLAY ===
class BorgGuardGUI(QtWidgets.QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle(CODENAME)
        self.setGeometry(100, 100, 800, 400)
        self.setStyleSheet("background-color: #0f0f0f; color: #00ffcc; font-family: Consolas;")
        self.layout = QtWidgets.QVBoxLayout()
        self.label = QtWidgets.QLabel("Awaiting live packets...")
        self.label.setAlignment(QtCore.Qt.AlignCenter)
        self.layout.addWidget(self.label)
        self.setLayout(self.layout)

    def update_status(self, packet_id, persona, threat, ancestry, ghost_sync):
        symbol = symbolic_feedback(threat)
        ghost_tag = "👻 GhostSync" if ghost_sync else ""
        status = f"{symbol} [{persona}] Packet {packet_id} → {threat} | Ancestry: {ancestry[:12]}... {ghost_tag}"
        self.label.setText(status)

# === PACKET HANDLER ===
def handle_packet(data):
    gui_ready.wait()
    payload = data[20:]
    if not payload: return
    packet_id = hashlib.md5(payload).hexdigest()[:8]
    persona = rotate_persona()
    ancestry = generate_ancestry(payload.hex())
    threat = classify_threat(payload)
    ghost_sync = detect_ghost_sync(payload)
    defense.ingest(packet_id, payload, threat)
    defense.mutate_codex(ghost_sync)
    if threat in ["Backdoor", "MAC/IP", "Personal"]:
        defense.dispatch(threat, payload)
    if is_personal_data(payload):
        defense.dispatch("Personal", payload)
    gui.update_status(packet_id, persona, threat, ancestry, ghost_sync)

# === GET ACTIVE INTERFACE IP ===
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return "127.0.0.1"

# === RAW SOCKET SNIFFER ===
def launch_sniffer():
    try:
        local_ip = get_local_ip()
        s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        s.bind((local_ip, 0))
        s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        s.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        while True:
            data, _ = s.recvfrom(65565)
            handle_packet(data)
    except Exception as e:
        print(f"[ERROR] Raw socket failed: {e}")
        print("💡 Tip: Disable Internet Connection Sharing and antivirus interference.")

# === FAKE TELEMETRY LOOP ===
def launch_fake_telemetry():
    while True:
        fake = generate_fake_telemetry()
        payload = str(fake).encode()
        defense.dispatch("FakeTelemetry", payload)
        defense.purge_expired()
        threading.Event().wait(10)

# === GUI THREAD ===
def launch_gui():
    global gui
    app = QtWidgets.QApplication([])
    gui = BorgGuardGUI()
    gui.show()
    gui_ready.set()
    app.exec_()

# === INIT ===
defense = DefenseCore()

if __name__ == "__main__":
    threading.Thread(target=launch_gui).start()
    threading.Thread(target=launch_sniffer).start()
    threading.Thread(target=launch_fake_telemetry).start()


