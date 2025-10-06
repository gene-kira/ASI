# 🧬 Glyph Mesh Visualizer: Autonomous Capsule Engine with Replicator Logic and Vault Protection

import sys, socket, threading, json, psutil, platform, hashlib, os
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QTextEdit, QPushButton, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, QTimer
from cryptography.fernet import Fernet

journal_file = "capsule_journal.json"
vault_file = "capsule_vault.json"
swarm_nodes = {}
capsule_engine = None

# 🔐 Vault Key (should be securely stored in production)
VAULT_KEY = Fernet.generate_key()
cipher = Fernet(VAULT_KEY)

def calculate_entropy():
    cpu = psutil.cpu_percent()
    mem = psutil.virtual_memory().percent
    return round((100 - cpu) * (100 - mem) / 100, 2)

def log_capsule(capsule_id, status="executed", impact=0, reason=None):
    entry = {
        "timestamp": datetime.utcnow().isoformat(),
        "node": platform.node(),
        "capsule": capsule_id,
        "status": status,
        "impact": impact,
        "reason": reason
    }
    with open(journal_file, "a") as f:
        f.write(json.dumps(entry) + "\n")

def send_to_node(node_ip, message):
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.sendto(message.encode(), (node_ip, 37020))

def trigger_swarm_echo(capsule_id, reason):
    echo = {
        "type": "swarm_echo",
        "capsule": capsule_id,
        "reason": reason,
        "timestamp": datetime.utcnow().isoformat()
    }
    for node in swarm_nodes:
        send_to_node(node, json.dumps(echo))

class CapsuleEngine:
    def __init__(self):
        self.mutations = []

    def ingest_capsule(self, node, message):
        try:
            capsule = json.loads(message)
            if self.check_self_destruct(capsule): return
            self.mutations.append(capsule)
            log_capsule(capsule["id"], status=capsule["status"], impact=capsule["impact"])
            self.replicate_capsule(capsule)
        except Exception as e:
            log_capsule("unknown", status="error", reason=str(e))

    def replicate_capsule(self, capsule):
        if capsule["impact"] < 20: return
        entropy = calculate_entropy()
        targets = [n for n in swarm_nodes if swarm_nodes[n]["impact"] < 50]
        for target in targets:
            replica = capsule.copy()
            replica["id"] += f"_replica_{target}"
            replica["replica_of"] = capsule["id"]
            replica["origin_entropy"] = entropy
            send_to_node(target, json.dumps(replica))
            log_capsule(replica["id"], status="replicated", impact=capsule["impact"])

    def check_self_destruct(self, capsule):
        now = datetime.utcnow().isoformat()
        entropy = calculate_entropy()
        valid_hash = capsule.get("hash", "").startswith("00")
        destruct = capsule.get("self_destruct", {})
        expired = now > destruct.get("expires_at", now)
        entropy_breach = entropy < destruct.get("min_entropy", 0)
        if expired or entropy_breach or not valid_hash:
            log_capsule(capsule["id"], status="self-destructed", impact=-10, reason="triggered")
            trigger_swarm_echo(capsule["id"], reason="destruct")
            return True
        return False

    def access_vault_capsule(self, entry):
        entropy = calculate_entropy()
        node = platform.node()
        valid_hash = entry["hash"].startswith("00")
        if entropy >= entry["min_entropy"] and node == entry["node_signature"] and valid_hash:
            try:
                decrypted = cipher.decrypt(entry["encrypted_payload"].encode()).decode()
                capsule = json.loads(decrypted)
                self.ingest_capsule(node, decrypted)
            except Exception as e:
                log_capsule(entry["id"], status="vault breach", impact=-20, reason=str(e))
                trigger_swarm_echo(entry["id"], reason="vault breach")
        else:
            log_capsule(entry["id"], status="vault breach", impact=-20, reason="validation failed")
            trigger_swarm_echo(entry["id"], reason="vault breach")

class GlyphVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        global capsule_engine
        capsule_engine = CapsuleEngine()

        self.setWindowTitle("🧠 Glyph Mesh Visualizer")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("background-color: #1e1e2f; color: #ffffff; font-family: Consolas;")

        layout = QVBoxLayout()
        self.label = QLabel(f"Swarm Node: {platform.node()} ({platform.system()})")
        self.label.setStyleSheet("color: #00ffcc; font-size: 18px;")
        layout.addWidget(self.label)

        self.telemetry = QLabel("")
        self.telemetry.setStyleSheet("font-size: 14px;")
        layout.addWidget(self.telemetry)

        self.scene = QGraphicsScene()
        self.view = QGraphicsView(self.scene)
        self.view.setStyleSheet("background-color: #0f0f1f;")
        layout.addWidget(self.view)

        self.journal = QTextEdit()
        self.journal.setReadOnly(True)
        self.journal.setStyleSheet("background-color: #0f0f1f; color: #ffffff; font-size: 12px;")
        layout.addWidget(self.journal)

        self.refresh_button = QPushButton("Refresh Journal")
        self.refresh_button.setStyleSheet("background-color: #00ffcc; color: #000000;")
        self.refresh_button.clicked.connect(self.load_journal)
        layout.addWidget(self.refresh_button)

        self.setLayout(layout)

        threading.Thread(target=self.listen_swarm, daemon=True).start()
        self.load_journal()
        self.update_telemetry()
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_telemetry)
        self.timer.start(5000)

    def update_telemetry(self):
        cpu = psutil.cpu_percent()
        mem = psutil.virtual_memory().percent
        entropy = calculate_entropy()
        self.telemetry.setText(f"CPU: {cpu}% | Memory: {mem}% | Entropy: {entropy}")
        self.render_glyphs()

    def load_journal(self):
        self.journal.clear()
        try:
            with open(journal_file, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    msg = f"[{entry['timestamp']}] {entry['node']} → {entry['capsule']} [{entry['status']}] Impact: {entry['impact']}"
                    if entry.get("reason"): msg += f" Reason: {entry['reason']}"
                    self.journal.append(msg)
        except Exception as e:
            self.journal.append(f"Error loading journal: {e}")

    def listen_swarm(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 37020))
        while True:
            data, addr = s.recvfrom(2048)
            node = addr[0]
            message = data.decode()
            if node not in swarm_nodes:
                swarm_nodes[node] = {"messages": [], "impact": 0}
            swarm_nodes[node]["messages"].append(message)
            swarm_nodes[node]["impact"] = min(100, swarm_nodes[node]["impact"] + 10)
            capsule_engine.ingest_capsule(node, message)

    def render_glyphs(self):
        self.scene.clear()
        radius_base = 30
        spacing = 100
        x, y = 50, 50
        for node, info in swarm_nodes.items():
            impact = info["impact"]
            radius = radius_base + impact // 5
            color = QColor(impact * 2 % 255, 255 - impact * 2 % 255, 100)
            glyph = QGraphicsEllipseItem(x, y, radius, radius)
            glyph.setBrush(QBrush(color))
            self.scene.addItem(glyph)
            label = self.scene.addText(node)
            label.setDefaultTextColor(Qt.white)
            label.setPos(x, y + radius + 5)
            x += spacing
            if x > 700:
                x = 50
                y += spacing

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = GlyphVisualizer()
    window.show()
    sys.exit(app.exec_())

