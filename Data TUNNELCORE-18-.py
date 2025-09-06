# 🔄 Autoloader
import sys, subprocess, importlib
def autoload(pkg): 
    try: return importlib.import_module(pkg)
    except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg]); return importlib.import_module(pkg)

np = autoload("numpy")
plt = autoload("matplotlib.pyplot")
psutil = autoload("psutil")
socket = autoload("socket")
threading = autoload("threading")

# 🔍 Port Scanner
def scan_ports(host="127.0.0.1", ports=range(1, 1024)):
    open_ports = []
    def scan(port):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            if s.connect_ex((host, port)) == 0:
                open_ports.append(port)
            s.close()
        except: pass

    threads = [threading.Thread(target=scan, args=(p,)) for p in ports]
    for t in threads: t.start()
    for t in threads: t.join()
    return open_ports

# 🧠 Decoy Pulse Logic
def get_decoy_personas():
    system_load = psutil.cpu_percent()
    personas = []
    if system_load > 50:
        personas.append("PulseEcho")
    if "Back4Blood.exe" in (p.name() for p in psutil.process_iter()):
        personas.append("SquadSyncBot")
    if system_load < 10:
        personas.append("GhostContact")
    return personas

# 🌀 Vortex Visualization
def draw_vortex(open_ports, decoys):
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_facecolor("black")
    ax.set_xlim(-1.2, 1.2)
    ax.set_ylim(-1.2, 1.2)
    ax.axis("off")

    rings = 12
    for i in range(rings):
        radius = 1 - i * 0.07
        ring_color = (0, 1, 1, 0.6 - i * 0.04)
        circle = plt.Circle((0, 0), radius, color=ring_color, fill=False, linewidth=2)
        ax.add_artist(circle)

    # 🔵 Port Pulses
    for idx, port in enumerate(open_ports):
        ring = idx % rings
        radius = 1 - ring * 0.07
        angle = 2 * np.pi * (port % 30) / 30
        x = radius * np.cos(angle)
        y = radius * np.sin(angle)
        ax.add_artist(plt.Circle((x, y), 0.02, color="deepskyblue"))

    # 🧿 Decoy Pulses
    for i, persona in enumerate(decoys):
        angle = 2 * np.pi * i / len(decoys)
        x = 0.3 * np.cos(angle)
        y = 0.3 * np.sin(angle)
        ax.add_artist(plt.Circle((x, y), 0.03, color="magenta"))
        ax.text(x, y, persona, color="white", fontsize=8, ha="center", va="center")

    # 🧵 Spiral Core
    theta = np.linspace(0, 4 * np.pi, 300)
    r = np.linspace(0.1, 1, 300)
    x = r * np.cos(theta)
    y = r * np.sin(theta)
    ax.plot(x, y, color="cyan", linewidth=1.5, alpha=0.6)

    ax.text(0, -1.15, "DATA TUNNELING", color="deepskyblue", fontsize=16,
            ha="center", va="center", fontweight="bold")
    plt.show()

# 🚀 Main Execution
if __name__ == "__main__":
    ports = scan_ports()
    decoys = get_decoy_personas()
    draw_vortex(ports, decoys)

