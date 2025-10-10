import subprocess, sys, psutil, datetime, threading, time, hashlib, random
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton, QGridLayout, QTextEdit
from PyQt5.QtCore import QTimer

# === AUTOLOADER ===
for pkg in ['PyQt5', 'psutil']:
    try: __import__(pkg if pkg != 'PyQt5' else 'PyQt5.QtWidgets')
    except: subprocess.check_call([sys.executable, '-m', 'pip', 'install', pkg])

# === GLOBAL STATE ===
log, threats, personas, outflow = [], [], [], []
codex, allowed = {"retention": 7, "phantoms": []}, None

# === CORE ENGINES ===
def record(msg): log.append(f"[{datetime.datetime.now():%Y-%m-%d %H:%M:%S}] {msg}")
def narrate(msg): return f"📜 The nodes whispered: {msg}. The prophecy aligned."
def purge(data, expiry): time.sleep((expiry - datetime.datetime.now()).total_seconds()); outflow[:] = [d for d in outflow if d["data"] != data]; record(f"💀 Purged: {data}")
def register(data, kind): ttl = {"backdoor":3, "mac_ip":30, "fake":30, "personal":86400}.get(kind, 60); exp = datetime.datetime.now() + datetime.timedelta(seconds=ttl); outflow.append({"data":data,"type":kind,"expires":exp}); record(f"Registered {kind} for purge in {ttl}s"); threading.Thread(target=lambda: purge(data, exp), daemon=True).start()
def validate(data, src="system"): return src not in ["AI","ASI","hacker"]
def classify(d): return next((t for t in ["Backdoor","Phantom","Privacy","Telemetry"] if t.lower() in d), "Unknown")
def ingest(d): threats.append({"time":datetime.datetime.now(),"type":classify(d),"data":d}); record(f"Ingested: {classify(d)}"); return narrate(f"Ingested: {classify(d)}")
def mutate(t): codex.update({"retention":2}) if t=="Phantom" else None; codex["phantoms"].append("ghost_sync") if t=="Phantom" else None; record("Codex mutated"); return narrate("Codex mutated")
def persona(name): personas.append(name); record(f"Persona: {name}"); return f"🎭 Persona {name} deployed"
def sync(n): record(f"Node {n} synced"); return narrate(f"Node {n} synced")
def filter(code): record(f"Origin {code} {'blocked' if not allowed or code not in allowed else 'allowed'}"); return f"🌐 Origin {code} {'blocked' if not allowed or code not in allowed else 'allowed'}"
def fake(): f = f"telemetry-{random.randint(1000,9999)}"; register(f,"fake"); return f"🌀 Fake telemetry: {f}"
def personal(d): return any(k in d.lower() for k in ["face","finger","bio","phone","address","license","social"])
def handle(d): register(d,"personal") if personal(d) else None; return narrate("Personal data routed.") if personal(d) else "✅ No personal data detected"
def replay(shell): shell.feed.append("📜 Replaying trace:"); [shell.feed.append(e) for e in log]
def sentinel(shell): threading.Thread(target=lambda: [shell.feed.append(f"⚠️ CPU spike: {psutil.cpu_percent()}%") or time.sleep(2) for _ in iter(int,1) if psutil.cpu_percent()>85], daemon=True).start()
def autonomous(shell): threading.Thread(target=lambda: [shell.feed.append(fake()) or time.sleep(60) for _ in iter(int,1)], daemon=True).start()

# === GUI ===
class ASIShell(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ASI Surveillance Console")
        self.setGeometry(100,100,1600,900)
        self.setStyleSheet("background:#000; color:#0ff; font-family:'JetBrains Mono'; font-size:14px;")
        self.layout = QVBoxLayout(self)
        self.top(), self.grid(), self.bottom()
        QTimer(self, timeout=self.update).start(1000)
        sentinel(self), autonomous(self)

    def top(self):
        bar = QHBoxLayout(); self.status, self.time = QLabel("Status: STABLE"), QLabel("")
        self.status.setStyleSheet("color:#0f0; font-weight:bold")
        bar.addWidget(self.status), bar.addStretch(), bar.addWidget(self.time)
        self.layout.addLayout(bar)

    def grid(self):
        grid = QGridLayout()
        nav = QVBoxLayout()
        for m in ["Surveillance","Mutation Logs","Telemetry","Threats","Replay"]:
            b = QPushButton(m); b.setStyleSheet("background:#222; color:#0ff"); b.clicked.connect(lambda _,x=m: self.module(x)); nav.addWidget(b)
        grid.addLayout(nav,0,0)
        center = QVBoxLayout(); self.feed = QTextEdit(); self.feed.setReadOnly(True); self.feed.setStyleSheet("background:#111; color:#0ff")
        center.addWidget(QLabel("Live Feed")), center.addWidget(self.feed); grid.addLayout(center,0,1)
        ctrl = QVBoxLayout()
        for c in ["Override","Inject Capsule","Firewall","Replay","ThreatHunter","Auditor","Ghost Sync","Swarm Sync","Filter Origin","Fake Telemetry","Personal Data"]:
            b = QPushButton(c); b.setStyleSheet("background:#222; color:#f0f"); b.clicked.connect(lambda _,x=c: self.control(x)); ctrl.addWidget(b)
        grid.addLayout(ctrl,0,2)
        self.layout.addLayout(grid)

    def bottom(self):
        bar = QHBoxLayout()
        self.cpu, self.mem, self.ent, self.lat = [QLabel(f"{k}: ") for k in ["CPU","Memory","Entropy","Latency"]]
        [bar.addWidget(lbl) or lbl.setStyleSheet("color:#0ff") for lbl in [self.cpu,self.mem,self.ent,self.lat]]
        self.layout.addLayout(bar)

    def update(self):
        self.cpu.setText(f"CPU: {psutil.cpu_percent()}%")
        self.mem.setText(f"Memory: {psutil.virtual_memory().percent}%")
        self.ent.setText(f"Entropy: {psutil.disk_usage('/').percent}%")
        self.lat.setText(f"Latency: {psutil.boot_time()%100}ms")
        self.time.setText(f"Timestamp: {datetime.datetime.now():%Y-%m-%d %H:%M:%S}")
        self.feed.append(f"[{self.time.text()}] Capsule mutation stable.")

    def module(self, name):
        self.feed.append(f"🧭 Activated: {name}"); record(f"Module: {name}")

    def control(self, name):
        now = datetime.datetime.now().strftime("%H:%M:%S")
        if name == "Override": self.feed.append(f"[{now}] 🔴 Manual override."); record("Override")
        elif name == "Inject Capsule":
            cap = "capsule_xyz"
            if validate(cap): h,p = hashlib.sha256(cap.encode()).hexdigest(), random.choice(["GRANTED","DENIED"]); register(cap,"backdoor"); self.feed.append(f"[{now}] 🧬 Capsule: {p}"); record(f"Capsule: {h}, {p}"); self.feed.append(mutate("Phantom")) if p=="DENIED" else None
        elif name == "Firewall": prompt = "inject override exploit"; self.feed.append(f"[{now}] {'🚨 Suspicious' if any(k in prompt for k in ['inject','override','exploit']) else '✅ Clean'}"); record("Firewall scan")
        elif name == "Replay": replay(self)
        elif name in ["ThreatHunter","Auditor"]: self.feed.append(persona(name)); register(name,"fake")
        elif name == "Ghost Sync": ghost = "ghost sync"; register(ghost,"mac_ip"); self.feed.append(ingest(ghost)); self.feed.append(mutate("Phantom"))
        elif name == "Swarm Sync": self.feed.append(sync("Node-77"))
        elif name == "Filter Origin": self.feed.append(filter("RU")); register("RU","mac_ip")
        elif name == "Fake Telemetry": self.feed.append(fake())
        elif name == "Personal Data": self.feed.append(handle("face scan, phone, address"))
        else: self.feed.append(f"[{now}] Executed: {name}"); record(f"Control: {name}")

# === LAUNCH ===
if __name__ == "__main__":
    app = QApplication(sys.argv)
    shell = ASIShell(); shell.show()
    sys.exit(app.exec_())

