# 🔮 Mythic OS Defense Engine — Unified Script

# ⚙️ AutoLoader
import subprocess, sys
def autoload_libs():
    required = {
        'psutil': 'psutil',
        'cryptography': 'cryptography',
        'cupy': 'cupy',
        'tkinter': 'tkinter'
    }
    for pkg, alias in required.items():
        try:
            __import__(alias)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
autoload_libs()

# 🔧 Imports
import tkinter as tk
import random, math, time, uuid, os, threading, socket
import psutil
import cupy as cp
from cryptography.fernet import Fernet

# 📜 Audit Scroll
def log_event(message):
    timestamp = time.strftime("%Y-%m-%d %H:%M:%S")
    print(f"[AuditScroll] 📜 {timestamp} — {message}")

# 🧠 ASI Logic Rewriter
agent_weights = cp.array([0.6, -0.8, -0.3])
rewrite_log = []

def asi_rewrite_module():
    global agent_weights
    mutation = cp.random.uniform(-0.3, 0.3, size=agent_weights.shape)
    agent_weights += mutation
    sigil = uuid.uuid4().hex[:6]
    rewrite_log.append({"sigil": sigil, "weights": agent_weights.get().tolist()})
    log_event(f"🧠 ASI rewrote logic — Sigil: {sigil}")
    return sigil

# 🧬 Self-Replicating Daemons
daemon_registry = []

class Daemon:
    def __init__(self, name, behavior):
        self.name = name
        self.behavior = behavior
        self.id = uuid.uuid4().hex[:6]

    def replicate(self):
        clone = Daemon(f"{self.name}_clone", self.behavior)
        daemon_registry.append(clone)
        log_event(f"🐉 Daemon replicated: {clone.name} ({clone.id})")

    def execute(self):
        log_event(f"🔧 Daemon executing: {self.name} ({self.id})")
        self.behavior()

def spawn_daemons():
    def behavior():
        score = psutil.cpu_percent()
        if score > 60:
            log_event(f"🔥 Daemon detected high CPU: {score}%")
    d = Daemon("Watcher", behavior)
    daemon_registry.append(d)
    threading.Thread(target=d.execute).start()
    threading.Thread(target=d.replicate).start()

# 🔐 Vault Encryption & Purging
vault_key = Fernet.generate_key()
vault_cipher = Fernet(vault_key)

def encrypt_vault_file(path):
    with open(path, 'rb') as f:
        data = f.read()
    encrypted = vault_cipher.encrypt(data)
    with open(path + ".vault", 'wb') as f:
        f.write(encrypted)
    os.remove(path)
    log_event(f"🔐 Vault encrypted: {path}")

def purge_vault(path):
    os.remove(path)
    log_event(f"💥 Vault purged: {path}")

def create_test_vault():
    path = f"vault_{uuid.uuid4().hex[:6]}.txt"
    with open(path, 'w') as f:
        f.write("Sensitive data: system keys, tokens, secrets.")
    encrypt_vault_file(path)
    return path + ".vault"

# 🛡️ Threat Neutralization
def neutralize_threats():
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        try:
            if proc.info['cpu_percent'] > 70:
                log_event(f"⚠️ Threat detected: {proc.info['name']} (PID {proc.info['pid']})")
                psutil.Process(proc.info['pid']).terminate()
                log_event(f"🚫 Threat neutralized: {proc.info['name']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue

# 🧠 Encrypted Memory Scanner
mem_key = Fernet.generate_key()
mem_cipher = Fernet(mem_key)

def scan_memory():
    mem = psutil.virtual_memory()
    snapshot = f"Total: {mem.total}, Used: {mem.used}, Free: {mem.available}"
    encrypted = mem_cipher.encrypt(snapshot.encode())
    log_event(f"🧠 Memory snapshot encrypted")
    return encrypted

def decrypt_memory(encrypted):
    return mem_cipher.decrypt(encrypted).decode()

# 🐝 Swarm Anomaly Triangulation
def swarm_score(vector):
    scores = []
    for _ in range(5):
        mutation = cp.random.uniform(-0.1, 0.1, size=agent_weights.shape)
        mutated = agent_weights + mutation
        score = cp.dot(cp.array(vector), mutated)
        scores.append(float(score.get()))
    avg = sum(scores) / len(scores)
    log_event(f"🐝 Swarm triangulated score: {avg:.2f}")
    return avg

# 🌐 Lightweight Network Monitor
def monitor_network():
    connections = psutil.net_connections(kind='inet')
    for conn in connections:
        laddr = f"{conn.laddr.ip}:{conn.laddr.port}" if conn.laddr else "N/A"
        raddr = f"{conn.raddr.ip}:{conn.raddr.port}" if conn.raddr else "N/A"
        status = conn.status
        log_event(f"🌐 Conn: {laddr} → {raddr} [{status}]")

# 🧿 Sigil Firewall Visualization
def draw_sigil(canvas, x, y, radius, color):
    canvas.create_oval(x - radius, y - radius, x + radius, y + radius,
                       outline=color, width=2)
    canvas.create_line(x - radius, y, x + radius, y, fill=color)
    canvas.create_line(x, y - radius, x, y + radius, fill=color)

def visualize_intrusion(canvas):
    x, y = random.randint(100, 680), random.randint(100, 420)
    draw_sigil(canvas, x, y, 30, "#FF0033")
    log_event(f"🔰 Intrusion visualized at ({x},{y})")

# 🌌 GUI Node Class
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        self.color = random.choice(["#00F7FF", "#FF00AA", "#FFD700"])

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width: self.dx *= -1
        if self.y <= 0 or self.y >= height: self.dy *= -1

    def draw(self):
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=self.color, outline=""
        )

# 🧙‍♂️ Mythic GUI
def launch_mythic_gui():
    root = tk.Tk()
    root.title("🛡️ Mythic OS Defense Engine")
    root.geometry("800x600")
    root.configure(bg="#0B0E1A")

    canvas = tk.Canvas(root, width=780, height=520, bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    nodes = [Node(canvas, 780, 520) for _ in range(40)]

    glyph_label = tk.Label(root, text="🧿 Glyph: None", font=("Arial", 12),
                           bg="#0B0E1A", fg="#00F7FF")
    glyph_label.pack()

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(780, 520)
            node.draw()
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill=n1.color, width=1)
        if random.random() < 0.05:
            visualize_intrusion(canvas)
        root.after(30, animate)

    def run_defense():
        neutralize_threats()
        vault_path = create_test_vault()
        purge_vault(vault_path)
        encrypted_mem = scan_memory()
        decrypted_mem = decrypt_memory(encrypted_mem)
        glyph = asi_rewrite_module()
        glyph_label.config(text=f"🧿 Glyph: {glyph}")
        log_event(f"🌀 Memory decrypted: {decrypted_mem}")
        spawn_daemons()
        vector = [random.uniform(-1, 1) for _ in range(3)]
        swarm_score(vector)

    btn_frame = tk.Frame(root, bg="#0B0E1A")
    btn_frame.pack(pady=10)

    tk.Button(btn_frame, text="🛡️ Run Defense Cycle", command=run_defense,
              font=("Arial", 12), bg="#1F2235", fg="#FFD700", padx=10, pady=5).pack(side="left", padx=10)

    tk.Button(btn_frame, text="🌐 Monitor Network", command=monitor_network,
              font=("Arial", 12), bg="#1F2235", fg="#00F7FF", padx=10, pady=5).pack(side="left", padx=10)

    animate()
    root.mainloop()

# 🚀 Launch the Mythic Defense Engine
if __name__ == "__main__":
    launch_mythic_gui()



