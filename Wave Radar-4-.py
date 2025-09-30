import sys, subprocess, threading, time, json, socket
import numpy as np
from collections import deque

# 🔧 Fallback Imports
def safe_import(lib, pip_name=None):
    try: return __import__(lib)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name or lib])
        return __import__(lib)

serial = safe_import("serial", "pyserial")
PyQt5 = safe_import("PyQt5")

from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QPushButton, QVBoxLayout, QHBoxLayout
from PyQt5.QtCore import Qt

# 🧠 Overlay Logic
def get_overlay_color(pressure):
    if pressure < 30: return "#00FF00"
    elif pressure < 70: return "#FFFF00"
    elif pressure < 90: return "#FF4500"
    else: return "#FF0000"

def get_glyph_for_state(state):
    return {
        "idle": "🟢", "normal": "🔵", "surge": "⚡", "overload": "🔥"
    }.get(state, "🔊")

# 📡 Serial Reader
def read_serial_telemetry(port="COM3", baudrate=9600):
    ser = serial.Serial(port, baudrate, timeout=1)
    while True:
        line = ser.readline().decode().strip()
        try:
            data = json.loads(line)
            voltage = float(data["voltage"])
            current = float(data["current"])
            power = voltage * current
            yield voltage, current, power
        except: continue

# 🌐 Ethernet Reader with Fallback Port Strategy
def read_ethernet_telemetry(host="0.0.0.0", ports=[5000, 5050, 5100]):
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

    for port in ports:
        try:
            sock.bind((host, port))
            print(f"🌐 Bound to port {port}")
            break
        except OSError as e:
            print(f"❌ Port {port} unavailable: {e}")
            continue
    else:
        print("🚫 No available ports. Exiting.")
        sys.exit(1)

    sock.listen(1)
    conn, addr = sock.accept()
    print(f"🔗 Connected to {addr}")
    while True:
        data = conn.recv(1024).decode().strip()
        try:
            packet = json.loads(data)
            voltage = float(packet["voltage"])
            current = float(packet["current"])
            power = voltage * current
            yield voltage, current, power
        except: continue

# 🧬 Classification + Pressure
event_log = deque(maxlen=100)

def classify_state(voltage, current, power):
    if power < 100: return "idle"
    elif power < 2000: return "normal"
    elif power < 3000: return "surge"
    else: return "overload"

def calculate_data_pressure(log, window=5):
    recent = list(log)[-window:]
    if not recent: return 0
    volume = len(recent)
    entropy = max([e['power'] for e in recent]) - min([e['power'] for e in recent])
    latency = np.std([e['power'] for e in recent])
    return (volume * 0.4) + (entropy * 0.4) + (latency * 0.2)

# 🖥️ GUI Shell
class RadarGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("⚡ Electrical Telemetry Radar")
        self.setGeometry(100, 100, 500, 300)

        self.layout = QVBoxLayout()
        self.overlay_label = QLabel("🧠 Overlay: Waiting for signal...")
        self.overlay_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.overlay_label)

        # Readout labels
        self.voltage_label = QLabel("🔢 Voltage: -- V")
        self.current_label = QLabel("🔢 Current: -- A")
        self.power_label = QLabel("🔢 Power: -- W")
        self.pressure_label = QLabel("🔴 Pressure: --")
        self.pressure_label.setAlignment(Qt.AlignCenter)

        readout_layout = QVBoxLayout()
        readout_layout.addWidget(self.voltage_label)
        readout_layout.addWidget(self.current_label)
        readout_layout.addWidget(self.power_label)
        readout_layout.addWidget(self.pressure_label)
        self.layout.addLayout(readout_layout)

        # Controls
        self.control_panel = QLabel("🎛️ Control Panel")
        self.layout.addWidget(self.control_panel)
        self.restart_btn = QPushButton("♻️ Restart")
        self.mute_btn = QPushButton("🔕 Mute")
        self.record_btn = QPushButton("🎙️ Record")
        self.escalate_btn = QPushButton("🚨 Escalate")
        self.layout.addWidget(self.restart_btn)
        self.layout.addWidget(self.mute_btn)
        self.layout.addWidget(self.record_btn)
        self.layout.addWidget(self.escalate_btn)

        self.setLayout(self.layout)

    def update_overlay(self, state, pressure, voltage, current, power):
        glyph = get_glyph_for_state(state)
        color = get_overlay_color(pressure)
        self.overlay_label.setText(f"{glyph} {state.upper()} | Pressure: {pressure:.1f}")
        self.overlay_label.setStyleSheet(f"color: {color}; font-size: 16px;")
        self.voltage_label.setText(f"🔢 Voltage: {voltage:.1f} V")
        self.current_label.setText(f"🔢 Current: {current:.1f} A")
        self.power_label.setText(f"🔢 Power: {power:.1f} W")
        self.pressure_label.setText(f"🔴 Pressure: {pressure:.1f}")
        self.pressure_label.setStyleSheet(f"color: {color}; font-size: 14px;")

# 🔊 Radar Loop
def run_radar(gui, mode="ethernet", port="COM3", baudrate=9600, eth_ports=[5000, 5050, 5100]):
    reader = read_serial_telemetry if mode == "serial" else lambda: read_ethernet_telemetry("0.0.0.0", eth_ports)
    for voltage, current, power in reader():
        start = time.time()
        state = classify_state(voltage, current, power)
        latency = time.time() - start
        event = {"voltage": voltage, "current": current, "power": power, "latency": latency}
        event_log.append(event)
        pressure = calculate_data_pressure(event_log)
        gui.update_overlay(state, pressure, voltage, current, power)

# 🚀 Main Launcher
def main():
    app = QApplication(sys.argv)
    gui = RadarGUI()

    def start_radar():
        run_radar(gui, mode="ethernet", port="COM3", baudrate=9600, eth_ports=[5000, 5050, 5100])

    radar_thread = threading.Thread(target=start_radar)
    radar_thread.start()

    gui.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
