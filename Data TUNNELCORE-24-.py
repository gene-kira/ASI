# 🔄 Autoloader
import sys, subprocess, importlib
def autoload(pkg): 
    try: return importlib.import_module(pkg)
    except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg]); return importlib.import_module(pkg)

np = autoload("numpy")
plt = autoload("matplotlib.pyplot")
animation = autoload("matplotlib.animation")
psutil = autoload("psutil")
socket = autoload("socket")
threading = autoload("threading")
time = autoload("time")

# 🧬 Data Packet Structure
class DataPacket:
    def __init__(self, content, tag, ttl):
        self.content = content
        self.tag = tag
        self.timestamp = time.time()
        self.ttl = ttl

    def is_expired(self):
        return time.time() - self.timestamp > self.ttl

# 🧹 Real-Time Data Vault
class DataVault:
    def __init__(self):
        self.packets = []
        self.purge_log = []

    def inject(self, content, tag, ttl):
        packet = DataPacket(content, tag, ttl)
        self.packets.append(packet)
        print(f"🧠 Injected [{tag}] → TTL: {ttl}s")

    def purge_expired(self):
        now = time.time()
        retained = []
        for p in self.packets:
            if p.is_expired():
                log = f"[{time.strftime('%H:%M:%S')}] Purged [{p.tag}] → {p.content}"
                self.purge_log.append(log)
                print(f"🔥 {log}")
            else:
                retained.append(p)
        self.packets = retained

vault = DataVault()

# 🛡️ Defense ASI Core
class DefenseASI:
    def __init__(self):
        self.modules = {"scanner": self.scan_processes, "rewriter": self.rewrite_logic}
        self.rewrite_log = []

    def scan_processes(self):
        threats = []
        for proc in psutil.process_iter(['name']):
            name = proc.info['name'].lower()
            if any(term in name for term in ["ai", "asi", "injector", "rogue", "sniffer", "backdoor"]):
                threats.append(name)
        return threats

    def rewrite_logic(self, threat_name):
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"[{timestamp}] Rewrote defense module in response to threat: {threat_name}"
        self.rewrite_log.append(log_entry)
        print(f"🛠️ {log_entry}")
        # Placeholder for actual code mutation logic

    def evolve(self):
        threats = self.scan_processes()
        for threat in threats:
            self.rewrite_logic(threat)

defense_node = DefenseASI()

# 🧠 Real-Time Decoy Persona Injection
def get_decoy_personas():
    system_load = psutil.cpu_percent()
    active_procs = [p.name().lower() for p in psutil.process_iter()]
    personas = []
    if system_load > 50: personas.append("PulseEcho")
    if any("back4blood" in name for name in active_procs): personas.append("SquadSyncBot")
    if system_load < 10: personas.append("GhostContact")
    if not personas: personas.append("LedgerPhantom")
    return personas

# 🔍 Real-Time Port Scanner
def scan_ports(host="127.0.0.1", ports=range(1, 1024)):
    open_ports = []
    def scan(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.3)
            if s.connect_ex((host, port)) == 0:
                open_ports.append(port)
            s.close()
        except: pass
    threads = [threading.Thread(target=scan, args=(p,)) for p in ports]
    for t in threads: t.start()
    for t in threads: t.join()
    return open_ports

# 🛡️ Real-Time MAC/IP Detection
def get_network_identifiers():
    for iface, addrs in psutil.net_if_addrs().items():
        for addr in addrs:
            if addr.family.name == 'AF_INET':
                vault.inject(addr.address, "IP Address", 30)
            elif addr.family.name == 'AF_PACKET':
                vault.inject(addr.address, "MAC Address", 30)

# 🔐 Personal Data Protection (1 Day TTL)
def scan_personal_data():
    sensitive_tags = ["face", "finger", "bio", "phone", "address", "license", "ssn"]
    for proc in psutil.process_iter(['name']):
        name = proc.info['name'].lower()
        if any(tag in name for tag in sensitive_tags):
            vault.inject(name, "Personal Data", 86400)

# 🛰️ Fake Telemetry Injection (30s TTL)
def inject_fake_telemetry():
    vault.inject("CPU=900%, RAM=999GB", "Fake Telemetry", 30)

# 🧬 Data Layer Mapping
data_layers = {
    0: "Sentinel Layer (Encryption & Defense)",
    1: "Network Telemetry",
    2: "System Metrics",
    3: "System Metrics",
    4: "Application State",
    5: "Application State",
    6: "Application State",
    7: "User Interaction",
    8: "User Interaction",
    9: "User Interaction",
    10: "Privacy-Sensitive",
    11: "Privacy-Sensitive"
}

# 🎨 Pulse Color Logic
def get_pulse_color(layer_index):
    if layer_index == 0: return "cyan"
    elif layer_index == 1: return "dodgerblue"
    elif layer_index in [2, 3]: return "lime"
    elif layer_index in [4, 5, 6]: return "orange"
    elif layer_index in [7, 8, 9]: return "gold"
    else: return "red"

# 🎞️ Visualization Setup
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_facecolor("black")
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis("off")

rings = 12
dots_per_ring = 30
pulse_objs = []
spiral_line, = ax.plot([], [], color="cyan", linewidth=1.5, alpha=0.6)
ax.text(0, -1.15, "DATA TUNNELING", color="deepskyblue", fontsize=16,
        ha="center", va="center", fontweight="bold")

# 🌀 Draw Rings and Pulses
for i in range(rings):
    radius = 1 - i * 0.07
    ring = plt.Circle((0, 0), radius, color=(0, 1, 1, 0.6 - i * 0.04), fill=False, linewidth=2)
    ax.add_artist(ring)
    ax.text(0, radius, data_layers[i], color="gray", fontsize=7, ha="center", va="bottom", alpha=0.5)

    pulse_color = get_pulse_color(i)
    for j in range(dots_per_ring):
        angle = 2 * np.pi * j / dots_per_ring
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        pulse = plt.Circle((x, y), 0.015, color=pulse_color)
        ax.add_artist(pulse)
        pulse_objs.append(pulse)

# 🧿 Decoy Personas (Real-Time)
decoys = get_decoy_personas()
print("🔐 Injecting Decoy Personas:", decoys)
for i, persona in enumerate(decoys):
    angle = 2 * np.pi * i / len(decoys)
    x = 0.3 * np.cos(angle)
    y = 0.3 * np.sin(angle)
    dot = plt.Circle((x, y), 0.03, color="magenta")
    ax.add_artist(dot)
    ax.text(x, y, persona, color="white", fontsize=8, ha="center", va="center")

# 🛡️ GUI Overlay
def draw_defense_gui():
    ax.text(-1.1, 1.1, "🛡️ Defense Node Active", color="cyan", fontsize=10, ha="left")
    ax.text(-1.1, 1.05, f"Zero Trust: Enabled", color="gray", fontsize=8, ha="left")

# 🛡️ GUI Overlay (continued)
def draw_defense_gui():
    ax.text(-1.1, 1.1, "🛡️ Defense Node Active", color="cyan", fontsize=10, ha="left")
    ax.text(-1.1, 1.05, "Zero Trust: Enabled", color="gray", fontsize=8, ha="left")
    ax.text(-1.1, 1.00, "Self-Rewrite: On Threat", color="gray", fontsize=8, ha="left")
    ax.text(-1.1, 0.95, f"Vault Size: {len(vault.packets)}", color="gray", fontsize=8, ha="left")
    if defense_node.rewrite_log:
        ax.text(-1.1, 0.90, f"Last Rewrite: {defense_node.rewrite_log[-1]}", color="magenta", fontsize=7, ha="left")

draw_defense_gui()

# 🔁 Animation Function
def animate(frame):
    vault.purge_expired()
    defense_node.evolve()

    # Update GUI overlay
    draw_defense_gui()

    # Spiral Core Animation
    theta = np.linspace(0, 4 * np.pi, 300)
    r = np.linspace(0.1, 1, 300)
    x = r * np.cos(theta + frame * 0.05)
    y = r * np.sin(theta + frame * 0.05)
    spiral_line.set_data(x, y)

    return [spiral_line]

# 🚀 Real-Time Ingest Initialization
scan_ports()
get_network_identifiers()
scan_personal_data()
inject_fake_telemetry()

# 🎬 Launch Animation
ani = animation.FuncAnimation(fig, animate, frames=300, interval=50, blit=True)
plt.show()

