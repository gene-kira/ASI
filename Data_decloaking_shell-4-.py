import sys, time, threading, subprocess, json, socket
import numpy as np

# === Autoloader Ritual ===
required_libs = {
    "PyQt5": "PyQt5",
    "serial": "pyserial",
    "numpy": "numpy"
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

# === Thresholds and Swarm Config ===
default_threshold = 3.3
recent_values = []
SWARM_NODES = ["192.168.1.101", "192.168.1.102"]
SWARM_PORT = 9090

# === Firewall Overlays ===
firewall_rules = {
    "serial:COM3": {"max_voltage": 6.0},
    "RJ45": {"allow": ["192.168.1.101", "192.168.1.102"]}
}

def enforce_firewall(source, value):
    rule = firewall_rules.get(source.split(":")[0], {})
    if "max_voltage" in rule and value > rule["max_voltage"]:
        symbol.setText(f"🛡️ BLOCKED: {source} > {value}V")
        symbol.setStyleSheet("color: orange; font-weight: bold; font-size: 18px;")
        print(f"[FIREWALL] ⚠️ Voltage breach on {source}: {value}V")

# === Persona Injection ===
def inject_persona(source, value):
    if source.startswith("serial") and value > 5.0:
        persona = "⚔️ Guardian"
    elif "RJ45" in source:
        persona = "🕸️ Weaver"
    else:
        persona = "👁️ Observer"
    watermark.setText(f"Persona Injected: {persona}")
    watermark.setStyleSheet("color: teal; font-style: italic; font-size: 16px;")
    return persona

# === Codex Mutation ===
def mutate_codex(persona):
    codex = {
        "⚔️ Guardian": {"threshold": 5.0, "color": "red"},
        "🕸️ Weaver": {"threshold": 0.0, "color": "purple"},
        "👁️ Observer": {"threshold": 3.3, "color": "blue"}
    }
    mutation = codex.get(persona, codex["👁️ Observer"])
    symbol.setStyleSheet(f"color: {mutation['color']}; font-weight: bold; font-size: 20px;")
    return mutation["threshold"]

# === Tensor Cognition ===
def tensor_cognition(values):
    if values:
        tensor = np.array(values).reshape(-1, 1)
        mean = np.mean(tensor)
        std = np.std(tensor)
        symbol.setText(f"🧠 Tensor Cognition: μ={mean:.2f}, σ={std:.2f}")
        symbol.setStyleSheet("color: cyan; font-style: italic; font-size: 16px;")

# === Swarm Sync ===
def sync_swarm(event):
    payload = json.dumps(event).encode()
    for node in SWARM_NODES:
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.sendto(payload, (node, SWARM_PORT))
            print(f"[SWARM] Synced to {node}")
        except Exception as e:
            print(f"[SWARM ERROR] {node}: {e}")

# === Daemon Trigger ===
def trigger_daemon(value, timestamp, source):
    event = {
        "type": "decloak",
        "value": value,
        "timestamp": timestamp,
        "source": source
    }
    with open("decloak_log.json", "a") as f:
        f.write(json.dumps(event) + "\n")
    subprocess.Popen([sys.executable, "daemon.py", str(value), timestamp, source])
    sync_swarm(event)

# === Decloaking Ritual ===
def decloak(value, source):
    enforce_firewall(source, value)
    persona = inject_persona(source, value)
    threshold = mutate_codex(persona)
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    symbol.setText(f"⚡ {source}: {value}V @ {timestamp}")
    recent_values.append(value)
    if len(recent_values) > 10:
        recent_values.pop(0)
    tensor_cognition(recent_values)
    trigger_daemon(value, timestamp, source)

# === Serial Monitoring ===
def monitor_port(port_name):
    try:
        ser = serial.Serial(port_name, 9600)
        print(f"[LISTENER] Bound to {port_name}")
        while True:
            raw = ser.readline().decode().strip()
            if raw:
                try:
                    value = float(raw)
                    decloak(value, f"serial:{port_name}")
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

# === RJ45 Mutation Simulation ===
def simulate_rj45_listener():
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind(("", SWARM_PORT))
        print(f"[RJ45] Listening on UDP port {SWARM_PORT}")
        while True:
            data, addr = sock.recvfrom(1024)
            src = addr[0]
            decloak(0, f"RJ45:{src}")
    except Exception as e:
        print(f"[RJ45 ERROR] {e}")

# === Launch Rituals ===
scan_and_bind_ports()
threading.Thread(target=simulate_rj45_listener, daemon=True).start()

# === Ritual Loop ===
sys.exit(app.exec_())
