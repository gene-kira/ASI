import sys, random, signal, socket, requests
from datetime import datetime
from PyQt5.QtWidgets import QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QScrollArea, QGraphicsOpacityEffect
from PyQt5.QtCore import QTimer, Qt, QThread, pyqtSignal, QPropertyAnimation
import serial.tools.list_ports, serial

# 🧠 Autoloader
def autoload(): import importlib, subprocess; [importlib.import_module(lib) if lib in sys.modules else subprocess.check_call([sys.executable, "-m", "pip", "install", lib]) for lib in ['serial','PyQt5']]
autoload()

# 🛡️ Interrupt Shield
signal.signal(signal.SIGINT, lambda s,f: print("\n🛡️ Interrupt blocked."))
signal.signal(signal.SIGTERM, lambda s,f: print("\n🛡️ Interrupt blocked."))

# 🔄 Telemetry Thread
class Telemetry(QThread): updated = pyqtSignal(dict)
def run(self): 
    while True:
        t = {}; ports = serial.tools.list_ports.comports()
        for p in ports:
            try: s = serial.Serial(p.device,9600,timeout=1); t[p.device]=s.readline().decode('utf-8','replace').strip() or "No data"; s.close()
            except Exception as e: t[p.device]=f"Error: {e}"
        self.updated.emit(t); self.msleep(2000)

# 🧠 Borg ASI Listener
class MemoryListener(QThread): packet = pyqtSignal(str)
def run(self): 
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM); sock.bind(("",9998))
    while True: self.packet.emit(sock.recvfrom(4096)[0].decode('utf-8','replace'))

# 🔧 Utilities
def api(): 
    try:
        r = requests.get("https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd", timeout=3)
        return f"BTC/USD: ${r.json()['bitcoin']['usd']}"
    except Exception as e:
        return f"API Error: {e}"

def log(layer,p,t): 
    try: open("mutation_log.txt","a",encoding="utf-8").write(f"{datetime.now()} | {layer} | {p} | {t}\n")
    except Exception as e: print(f"[Log Error] {e}")

def broadcast(layer,p,t): 
    try: socket.socket(socket.AF_INET,socket.SOCK_DGRAM).sendto(f"{datetime.now()}|{layer}|{p}|{t}".encode(),("255.255.255.255",9998))
    except Exception as e: print(f"[Broadcast Error] {e}")

def escalate(layer,p,t): 
    if p=="Negative" and "Error" in t: print(f"[Security Cortex] 🚨 {layer} escalation"); broadcast(layer,p,t)

# 🧩 Layer Widget
class Layer(QWidget):
    def __init__(self,name,desc,color,overlay):
        super().__init__()
        self.name,self.desc,self.overlay_text = name,desc,overlay
        self.layout = QVBoxLayout(self)
        row = QHBoxLayout(); self.label = QLabel(f"{name} ─ {desc}"); self.label.setStyleSheet("color:white;font-weight:bold")
        self.polarity = QLabel(); self.polarity.setFixedWidth(120); self.polarity.setAlignment(Qt.AlignCenter)
        row.addWidget(self.label); row.addWidget(self.polarity)
        self.overlay = QLabel(f"Overlay: {overlay}"); self.overlay.setStyleSheet("color:#00CED1;font-style:italic")
        self.api_data = QLabel("API: [pending]"); self.api_data.setStyleSheet("color:#FFD700")
        self.telemetry = QLabel("Telemetry: [pending]"); self.telemetry.setStyleSheet("color:gray"); self.telemetry.setWordWrap(True)
        self.quantum_overlay = QLabel("Quantum Overlay: [pending]"); self.quantum_overlay.setStyleSheet("color:#7FFFD4;font-style:italic")
        self.layout.addLayout(row)
        self.layout.addWidget(self.overlay)
        self.layout.addWidget(self.api_data)
        self.layout.addWidget(self.telemetry)
        self.layout.addWidget(self.quantum_overlay)
        self.update_polarity()

    def animate(self): 
        e = QGraphicsOpacityEffect(); self.polarity.setGraphicsEffect(e)
        a = QPropertyAnimation(e,b"opacity"); a.setDuration(1000); a.setStartValue(0.0); a.setEndValue(1.0); a.start()

    def update_quantum_overlay(self):
        overlays = [
            "Bloch vector → |0⟩",
            "Superposition → α|0⟩ + β|1⟩",
            "Entangled → ψ_AB = α|00⟩ + β|11⟩",
            "Decoherence → mixed state"
        ]
        self.quantum_overlay.setText(f"Quantum Overlay: {random.choice(overlays)}")

    def update_polarity(self):
        p = random.choice(["Positive","Neutral","Negative"])
        self.polarity.setText(f"🞄 {p}")
        self.polarity.setStyleSheet(f"background-color:{dict(Positive='#0F0',Neutral='#FF0',Negative='#F00')[p]};color:black;font-weight:bold")
        self.animate(); broadcast(self.name,p,"mutation"); self.api_data.setText(api()); self.current_polarity = p
        self.update_quantum_overlay()

    def update_telemetry(self,t):
        try: ts = str(t).encode('utf-8','replace').decode('utf-8'); self.telemetry.setText(f"Telemetry: {ts}")
        except Exception as e: ts = f"Error: {e}"; self.telemetry.setText(ts)
        log(self.name,self.current_polarity,ts); escalate(self.name,self.current_polarity,ts)

# 🧠 Dashboard
class Dashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Borg ASI Shell"); self.setStyleSheet("background-color:#1e1e1e")
        scroll = QScrollArea(); scroll.setWidgetResizable(True); container = QWidget(); layout = QVBoxLayout(container)
        self.layers = []
        for name,desc,color,overlay in [
            ("🧠 Conceptual","User behavior → Meaning → Insight","#0FF","🧭 Behavioral Mapping"),
            ("💾 Digital","APIs → JSON → Structured pipelines","#0BF","📦 Format Mutation"),
            ("⚙️ Physical","Cloud → CDN → Fiber optics","#FA0","🛰️ Transmission Pathways"),
            ("🔬 Atomic","Photons → Electrons → Qubits","#808","⚛️ Quantum Signaling"),
            ("🧩 Symbolic","Tags → Metadata → Semantic cognition","#0F0","🧠 Semantic Web Threads"),
            ("🔐 Security","HTTPS → OAuth → Anomaly detection","#F00","🔐 Threat Shielding")
        ]: l = Layer(name,desc,color,overlay); layout.addWidget(l); self.layers.append(l)
        container.setLayout(layout); scroll.setWidget(container); main = QVBoxLayout(self); main.addWidget(scroll)
        self.timer = QTimer(); self.timer.timeout.connect(self.mutate); self.timer.start(3000)
        self.telemetry = Telemetry(); self.telemetry.updated.connect(self.update_all); self.telemetry.start()
        self.listener = MemoryListener(); self.listener.packet.connect(lambda p: print(f"[Swarm Sync] 🧠 {p}")); self.listener.start()

    def mutate(self): [l.update_polarity() for l in self.layers]
    def update_all(self,t): [l.update_telemetry(t) for l in self.layers]

# 🚀 Launch
if __name__ == "__main__":
    app = QApplication(sys.argv); dash = Dashboard(); dash.resize(1000,600); dash.show(); sys.exit(app.exec_())
