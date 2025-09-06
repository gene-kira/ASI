# 🔄 Autoloader for required libraries
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
    if layer_index == 0: return "cyan"         # Sentinel Layer
    elif layer_index == 1: return "dodgerblue" # Network
    elif layer_index in [2, 3]: return "lime"  # System Metrics
    elif layer_index in [4, 5, 6]: return "orange" # App State
    elif layer_index in [7, 8, 9]: return "gold"   # User Interaction
    else: return "red"                        # Privacy-Sensitive

# 🔍 Real-time Port Scanner
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

# 🧠 Genre-Aware Decoy Injection
def get_decoy_personas():
    system_load = psutil.cpu_percent()
    active_procs = [p.name().lower() for p in psutil.process_iter()]
    personas = []
    if system_load > 50: personas.append("PulseEcho")
    if any("back4blood" in name for name in active_procs): personas.append("SquadSyncBot")
    if system_load < 10: personas.append("GhostContact")
    if not personas: personas.append("LedgerPhantom")
    return personas

# 🎞️ Animation Setup
fig, ax = plt.subplots(figsize=(8, 8))
ax.set_facecolor("black")
ax.set_xlim(-1.2, 1.2)
ax.set_ylim(-1.2, 1.2)
ax.axis("off")

rings = 12
dots_per_ring = 30
ring_objs = []
pulse_objs = []
spiral_line, = ax.plot([], [], color="cyan", linewidth=1.5, alpha=0.6)
label = ax.text(0, -1.15, "DATA TUNNELING", color="deepskyblue", fontsize=16,
                ha="center", va="center", fontweight="bold")

# 🌀 Draw Concentric Rings
for i in range(rings):
    radius = 1 - i * 0.07
    ring = plt.Circle((0, 0), radius, color=(0, 1, 1, 0.6 - i * 0.04), fill=False, linewidth=2)
    ax.add_artist(ring)
    ring_objs.append(ring)

    # 🏷️ Optional Ring Labels
    ax.text(0, radius, data_layers[i], color="gray", fontsize=7, ha="center", va="bottom", alpha=0.5)

# 🔵 Create Anchored Pulses on Each Ring with Data Mapping
for i in range(rings):
    radius = 1 - i * 0.07
    pulse_color = get_pulse_color(i)
    for j in range(dots_per_ring):
        angle = 2 * np.pi * j / dots_per_ring
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        pulse = plt.Circle((x, y), 0.015, color=pulse_color)
        ax.add_artist(pulse)
        pulse_objs.append(pulse)

# 🧿 Decoy Pulse Labels + Logging
decoys = get_decoy_personas()
print("🔐 Injecting Decoy Personas:", decoys)
for i, persona in enumerate(decoys):
    angle = 2 * np.pi * i / len(decoys)
    x = 0.3 * np.cos(angle)
    y = 0.3 * np.sin(angle)
    dot = plt.Circle((x, y), 0.03, color="magenta")
    ax.add_artist(dot)
    ax.text(x, y, persona, color="white", fontsize=8, ha="center", va="center")

# 🔁 Animation Function
def animate(frame):
    # Spiral Core Animation
    theta = np.linspace(0, 4 * np.pi, 300)
    r = np.linspace(0.1, 1, 300)
    x = r * np.cos(theta + frame * 0.05)
    y = r * np.sin(theta + frame * 0.05)
    spiral_line.set_data(x, y)
    return [spiral_line]

# 🎬 Launch Animation
ani = animation.FuncAnimation(fig, animate, frames=300, interval=50, blit=True)
plt.show()

