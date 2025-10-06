# 🧬 PyQt Glyph Mesh Visualizer: Swarm-Synced, Capsule-Aware
import sys, socket, threading, json, psutil, platform
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QTextEdit, QPushButton, QGraphicsScene, QGraphicsView, QGraphicsEllipseItem
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtCore import Qt, QTimer

journal_file = "capsule_journal.json"
swarm_nodes = {}

class GlyphVisualizer(QWidget):
    def __init__(self):
        super().__init__()
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
        entropy = round((100 - cpu) * (100 - mem) / 100, 2)
        self.telemetry.setText(f"CPU: {cpu}% | Memory: {mem}% | Entropy: {entropy}")
        self.render_glyphs()

    def load_journal(self):
        self.journal.clear()
        try:
            with open(journal_file, "r") as f:
                for line in f:
                    entry = json.loads(line)
                    msg = f"[{entry['timestamp']}] {entry['node']} → {entry['capsule']} [{entry['status']}] Impact: {entry['impact']}\n"
                    self.journal.append(msg)
        except Exception as e:
            self.journal.append(f"Error loading journal: {e}")

    def listen_swarm(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.bind(('', 37020))
        while True:
            data, addr = s.recvfrom(1024)
            node = addr[0]
            message = data.decode()
            if node not in swarm_nodes:
                swarm_nodes[node] = {"messages": [], "impact": 0}
            swarm_nodes[node]["messages"].append(message)
            swarm_nodes[node]["impact"] = min(100, swarm_nodes[node]["impact"] + 10)

    def render_glyphs(self):
        self.scene.clear()
        radius = 30
        spacing = 100
        x, y = 50, 50
        for node, info in swarm_nodes.items():
            impact = info["impact"]
            color = QColor(0, min(impact * 2, 255), 255 - min(impact * 2, 255))
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

