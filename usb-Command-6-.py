import sys, random, signal, socket, requests
from datetime import datetime

# 🧠 Autoloader
def autoload_libraries():
    import importlib
    required = ['serial', 'PyQt5']
    for lib in required:
        try:
            importlib.import_module(lib)
        except ImportError:
            import subprocess
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libraries()

# 🛡️ Interrupt Shield
def block_interrupt(signum, frame):
    print("\n🛡️ Interrupt blocked. EchoNull shell remains active.")

signal.signal(signal.SIGINT, block_interrupt)
signal.signal(signal.SIGTERM, block_interrupt)

from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QScrollArea, QGraphicsOpacityEffect
)
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QPropertyAnimation
import serial.tools.list_ports
import serial

# 🔄 Telemetry Worker
class TelemetryWorker(QThread):
    telemetry_updated = pyqtSignal(dict)

    def run(self):
        while True:
            telemetry = {}
            ports = serial.tools.list_ports.comports()
            for port in ports:
                try:
                    ser = serial.Serial(port.device, baudrate=9600, timeout=1)
                    line = ser.readline().decode('utf-8', errors='replace').strip()
                    telemetry[port.device] = line if line else "No data"
                    ser.close()
                except Exception as e:
                    telemetry[port.device] = f"Error: {str(e)}"
            self.telemetry_updated.emit(telemetry)
            self.msleep(2000)

# 🌐 API Feed
def fetch_api_data():
    try:
        r = requests.get("https://api.coindesk.com/v1/bpi/currentprice.json", timeout=3)
        return f"BTC/USD: {r.json()['bpi']['USD']['rate']}"
    except Exception as e:
        return f"API Error: {e}"

# 🔥 Daemon Trigger
def trigger_daemon(layer_name, polarity):
    if polarity == "Negative":
        print(f"[Daemon Trigger] ⚠️ {layer_name} breached polarity threshold!")

# 📜 Forensic Logger
def log_mutation(layer_name, polarity, telemetry):
    try:
        with open("mutation_log.txt", "a", encoding="utf-8") as log:
            log.write(f"{datetime.now()} | {layer_name} | Polarity: {polarity} | Telemetry: {telemetry}\n")
    except Exception as e:
        print(f"[Logging Error] {e}")

# 🧠 Swarm Sync
def broadcast_mutation(message):
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        sock.sendto(message.encode(), ("255.255.255.255", 9999))
    except Exception as e:
        print(f"[Swarm Error] {e}")

# 🧩 Layer Widget
class DataLayerWidget(QWidget):
    def __init__(self, name, description, base_color, overlay_text):
        super().__init__()
        self.name = name
        self.description = description
        self.base_color = base_color
        self.overlay_text = overlay_text
        self.init_ui()

    def init_ui(self):
        self.layout = QVBoxLayout()

        top_row = QHBoxLayout()
        self.label = QLabel(f"{self.name} ─ {self.description}")
        self.label.setStyleSheet("color: white; font-weight: bold;")
        self.polarity = QLabel()
        self.polarity.setFixedWidth(120)
        self.polarity.setAlignment(Qt.AlignCenter)
        top_row.addWidget(self.label)
        top_row.addWidget(self.polarity)

        self.overlay = QLabel(f"Overlay: {self.overlay_text}")
        self.overlay.setStyleSheet("color: #00CED1; font-style: italic;")

        self.api_data = QLabel("API: [pending]")
        self.api_data.setStyleSheet("color: #FFD700;")

        self.telemetry = QLabel("Telemetry: [pending]")
        self.telemetry.setStyleSheet("color: gray;")
        self.telemetry.setWordWrap(True)

        self.layout.addLayout(top_row)
        self.layout.addWidget(self.overlay)
        self.layout.addWidget(self.api_data)
        self.layout.addWidget(self.telemetry)
        self.setLayout(self.layout)

        self.update_polarity()

    def animate_polarity(self):
        effect = QGraphicsOpacityEffect()
        self.polarity.setGraphicsEffect(effect)
        anim = QPropertyAnimation(effect, b"opacity")
        anim.setDuration(1000)
        anim.setStartValue(0.0)
        anim.setEndValue(1.0)
        anim.start()

    def update_polarity(self):
        polarity_state = random.choice(["Positive", "Neutral", "Negative"])
        color_map = {
            "Positive": "#00FF00",
            "Neutral": "#FFFF00",
            "Negative": "#FF0000"
        }
        self.polarity.setText(f"🞄 {polarity_state}")
        self.polarity.setStyleSheet(f"background-color: {color_map[polarity_state]}; color: black; font-weight: bold;")
        self.animate_polarity()
        trigger_daemon(self.name, polarity_state)
        broadcast_mutation(f"{self.name} polarity → {polarity_state}")
        self.current_polarity = polarity_state
        self.api_data.setText(fetch_api_data())

    def update_telemetry(self, telemetry):
        try:
            telemetry_str = str(telemetry).encode('utf-8', errors='replace').decode('utf-8')
            self.telemetry.setText(f"Telemetry: {telemetry_str}")
            log_mutation(self.name, self.current_polarity, telemetry_str)
        except Exception as e:
            self.telemetry.setText(f"Telemetry Error: {str(e)}")

# 🧠 Dashboard
class DataDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Mythic Data Cognition Shell")
        self.setStyleSheet("background-color: #1e1e1e;")

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        container = QWidget()
        container_layout = QVBoxLayout(container)

        self.layers = []
        self.add_layer(container_layout, "🧠 Conceptual", "User behavior → Meaning → Insight", "#00FFFF", "🧭 Behavioral Mapping")
        self.add_layer(container_layout, "💾 Digital", "APIs → JSON → Structured pipelines", "#00BFFF", "📦 Format Mutation")
        self.add_layer(container_layout, "⚙️ Physical", "Cloud → CDN → Fiber optics", "#FFA500", "🛰️ Transmission Pathways")
        self.add_layer(container_layout, "🔬 Atomic", "Photons → Electrons → Qubits", "#800080", "⚛️ Quantum Signaling")
        self.add_layer(container_layout, "🧩 Symbolic", "Tags → Metadata → Semantic cognition", "#00FF00", "🧠 Semantic Web Threads")
        self.add_layer(container_layout, "🔐 Security", "HTTPS → OAuth → Anomaly detection", "#FF0000", "🔐 Threat Shielding")

        container.setLayout(container_layout)
        scroll.setWidget(container)

        main_layout = QVBoxLayout()
        main_layout.addWidget(scroll)
        self.setLayout(main_layout)

        self.timer = QTimer()
        self.timer.timeout.connect(self.mutate_layers)
        self.timer.start(3000)

        self.telemetry_thread = TelemetryWorker()
        self.telemetry_thread.telemetry_updated.connect(self.update_telemetry_all)
        self.telemetry_thread.start()

    def add_layer(self, layout, name, description, color, overlay):
        layer = DataLayerWidget(name, description, color, overlay)
        layout.addWidget(layer)
        self.layers.append(layer)

    def mutate_layers(self):
        for layer in self.layers:
            layer.update_polarity()

    def update_telemetry_all(self, telemetry):
        for layer in self.layers:
            layer.update_telemetry(telemetry)

# 🚀 Launch
if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = DataDashboard()
    dashboard.resize(1000, 600)
    dashboard.show()
    sys.exit(app.exec_())
