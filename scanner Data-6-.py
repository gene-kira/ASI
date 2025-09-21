import sys
import subprocess
import importlib
import logging
import socket
import struct
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QPushButton, QTextEdit, QComboBox, QHBoxLayout
)
from PyQt6.QtGui import QColor
from PyQt6.QtCore import QTimer

# 🧠 Autoloader Daemon
def autoload(libraries):
    for lib in libraries:
        try:
            importlib.import_module(lib)
            logging.info(f"✅ Library '{lib}' already present.")
        except ImportError:
            logging.info(f"🔧 Installing: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
            logging.info(f"✅ Installed: {lib}")

required_libraries = ["pyqt6"]
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
autoload(required_libraries)

# 🌐 Auto-Detect Host IP
def get_local_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"

# 🧬 Symbolic Anomaly Prediction Engine
def predict_entropy(pkt_len, proto_id):
    proto_score = {6: 0.9, 17: 0.7}.get(proto_id, 0.3)
    entropy = pkt_len / 1500 + (1 - proto_score)
    if entropy < 0.5:
        return "Normal", "blue"
    elif entropy < 1.0:
        return "Drifting", "orange"
    else:
        return "Abnormal", "red"

# 🔍 Packet Dissection Daemon
packet_log = []

def dissect_packet(data):
    if len(data) < 20:
        return
    ip_header = struct.unpack('!BBHHHBBH4s4s', data[:20])
    proto_id = ip_header[6]
    src_ip = socket.inet_ntoa(ip_header[8])
    dst_ip = socket.inet_ntoa(ip_header[9])
    pkt_len = len(data)
    status, color = predict_entropy(pkt_len, proto_id)
    proto_name = {6: "TCP", 17: "UDP"}.get(proto_id, "Other")
    story = f"🧠 Glyph: {proto_name} flow from {src_ip} to {dst_ip} | Status: {status} | Entropy: {round(pkt_len/1500,2)}"
    packet_log.append((story, color))

def start_capture_loop():
    try:
        host_ip = get_local_ip()
        sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
        sock.bind((host_ip, 0))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
        sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
        return sock
    except Exception as e:
        packet_log.append((f"⚠️ Error initializing capture: {e}", "red"))
        return None

# 🖥️ Scientific Cognition Lab GUI
class CognitionLab(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧪 Sovereign Cognition Lab")
        self.setGeometry(100, 100, 900, 700)
        self.layout = QVBoxLayout()

        self.label = QLabel("Live Glyph Feed:")
        self.layout.addWidget(self.label)

        self.feed = QTextEdit()
        self.feed.setReadOnly(True)
        self.layout.addWidget(self.feed)

        self.control_panel = QHBoxLayout()
        self.color_filter = QComboBox()
        self.color_filter.addItems(["All", "blue", "orange", "red"])
        self.color_filter.currentTextChanged.connect(self.filter_feed)
        self.control_panel.addWidget(QLabel("🎛️ Filter by Color:"))
        self.control_panel.addWidget(self.color_filter)

        self.override_button = QPushButton("🗳️ Trigger Override Ritual")
        self.override_button.clicked.connect(self.trigger_override)
        self.control_panel.addWidget(self.override_button)

        self.layout.addLayout(self.control_panel)

        self.scan_button = QPushButton("🔬 Start Continuous Packet Dissection")
        self.scan_button.clicked.connect(self.start_sniffing)
        self.layout.addWidget(self.scan_button)

        self.setLayout(self.layout)
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_feed)
        self.filtered_color = "All"
        self.capture_socket = None

    def start_sniffing(self):
        self.feed.append("🔍 Continuous cognition initiated...")
        self.capture_socket = start_capture_loop()
        self.timer.start(1000)

    def update_feed(self):
        if self.capture_socket:
            try:
                data = self.capture_socket.recvfrom(65565)[0]
                dissect_packet(data)
            except Exception as e:
                packet_log.append((f"⚠️ Socket error: {e}", "red"))
        if packet_log:
            story, color = packet_log.pop(0)
            if self.filtered_color == "All" or self.filtered_color == color:
                self.feed.setTextColor(QColor(color))
                self.feed.append(story)

    def filter_feed(self, color):
        self.filtered_color = color

    def trigger_override(self):
        self.feed.append("🗳️ Executive override ritual triggered. Glyphs await reclassification...")

# 🧠 Launch GUI
if __name__ == "__main__":
    app = QApplication(sys.argv)
    lab = CognitionLab()
    lab.show()
    sys.exit(app.exec())

