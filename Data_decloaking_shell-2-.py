import sys, time, threading, subprocess, json

# === Autoloader Ritual ===
required_libs = {
    "PyQt5": "PyQt5",
    "serial": "pyserial"
}

def autoload_libraries():
    for lib, pip_name in required_libs.items():
        try:
            __import__(lib)
            print(f"[AUTOLOADER] ✅ {lib} loaded")
        except ImportError:
            print(f"[AUTOLOADER] ⚠️ {lib} missing — invoking ritual install")
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
            print(f"[AUTOLOADER] 🔁 {lib} installed and ready")

autoload_libraries()

# === Imports after autoload ===
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QVBoxLayout
import serial, serial.tools.list_ports

# === GUI Initialization ===
app = QApplication([])
window = QWidget()
layout = QVBoxLayout()

symbol = QLabel("🧿 Awaiting anomaly…")
symbol.setStyleSheet("font-size: 24px; color: gray;")
layout.addWidget(symbol)

watermark = QLabel("🧿 Cognition Active")
watermark.setStyleSheet("color: blue; font-style: italic;")
layout.addWidget(watermark)

window.setLayout(layout)
window.setWindowTitle("Symbolic Decloaking Shell")
window.show()

# === Decloaking Ritual ===
threshold = 3.3  # Voltage threshold for anomaly

def decloak(value, port):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    symbol.setText(f"⚡ {port}: {value}V @ {timestamp}")
    symbol.setStyleSheet("color: red; font-weight: bold; font-size: 24px;")
    trigger_daemon(value, timestamp, port)

# === Daemon Trigger ===
def trigger_daemon(value, timestamp, port):
    event = {
        "type": "decloak",
        "value": value,
        "timestamp": timestamp,
        "source": port
    }
    with open("decloak_log.json", "a") as f:
        f.write(json.dumps(event) + "\n")

    subprocess.Popen([sys.executable, "daemon.py", str(value), timestamp, port])

# === Multi-Port Listener ===
def monitor_port(port_name):
    try:
        ser = serial.Serial(port_name, 9600)
        print(f"[LISTENER] Bound to {port_name}")
        while True:
            raw = ser.readline().decode().strip()
            if raw:
                try:
                    value = float(raw)
                    if value > threshold:
                        decloak(value, port_name)
                except ValueError:
                    print(f"[WARN] Non-numeric input on {port_name}: {raw}")
    except Exception as e:
        print(f"[ERROR] {port_name}: {e}")

def scan_and_bind_ports():
    ports = serial.tools.list_ports.comports()
    if not ports:
        symbol.setText("⚠️ No serial ports detected")
        symbol.setStyleSheet("color: orange; font-weight: bold;")
    for port in ports:
        threading.Thread(target=monitor_port, args=(port.device,), daemon=True).start()

scan_and_bind_ports()

# === Ritual Loop ===
sys.exit(app.exec_())
