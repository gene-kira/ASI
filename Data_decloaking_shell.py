# symbolic_decloaking_shell.py

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
import serial

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

def decloak(value):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    symbol.setText(f"⚡ Decloaked: {value}V @ {timestamp}")
    symbol.setStyleSheet("color: red; font-weight: bold; font-size: 24px;")
    trigger_daemon(value, timestamp)

# === Daemon Trigger ===
def trigger_daemon(value, timestamp):
    event = {
        "type": "decloak",
        "value": value,
        "timestamp": timestamp,
        "source": "serial:COM3"
    }
    with open("decloak_log.json", "a") as f:
        f.write(json.dumps(event) + "\n")

    subprocess.Popen(["python", "daemon.py", str(value), timestamp])

# === Telemetry Listener ===
def telemetry_listener():
    try:
        ser = serial.Serial('COM3', 9600)
        while True:
            raw = ser.readline().decode().strip()
            if raw:
                value = float(raw)
                if value > threshold:
                    decloak(value)
    except Exception as e:
        symbol.setText(f"⚠️ Telemetry Error: {e}")
        symbol.setStyleSheet("color: orange; font-weight: bold;")

threading.Thread(target=telemetry_listener, daemon=True).start()

# === Ritual Loop ===
sys.exit(app.exec_())
