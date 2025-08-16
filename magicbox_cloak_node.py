# 🔧 Auto-install required libraries
try:
    import tkinter as tk
    from tkinter import Canvas
    import socket, struct, threading, time, uuid, os
    import geoip2.database
    from cryptography.fernet import Fernet
except ImportError:
    import subprocess
    import sys
    subprocess.check_call([sys.executable, "-m", "pip", "install", "cryptography", "geoip2"])
    import tkinter as tk
    from tkinter import Canvas
    import socket, struct, threading, time, uuid, os
    import geoip2.database
    from cryptography.fernet import Fernet

# 🧩 Mutation Hooks
class MutationHooks:
    def __init__(self, gui=None):
        self.gui = gui

    def log(self, msg):
        print(f"[Mutation] {msg}")
        if self.gui:
            self.gui.update_status(msg)

# 🔍 Packet Sniffer (Raw Socket)
class PacketSniffer:
    def __init__(self, iface=None, mutator=None):
        self.iface = iface or socket.gethostbyname(socket.gethostname())
        self.mutator = mutator

    def start(self):
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_IP)
            sock.bind((self.iface, 0))
            sock.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            sock.ioctl(socket.SIO_RCVALL, socket.RCVALL_ON)
            self.mutator.log("Packet sniffer started")
            while True:
                packet, _ = sock.recvfrom(65565)
                self.process(packet)
        except Exception as e:
            self.mutator.log(f"Sniffer error: {e}")

    def process(self, packet):
        iph = struct.unpack("!BBHHHBBH4s4s", packet[0:20])
        protocol = iph[6]
        src_ip = socket.inet_ntoa(iph[8])
        dst_ip = socket.inet_ntoa(iph[9])
        if protocol == 6:
            self.mutator.log(f"TCP: {src_ip} → {dst_ip}")
        elif protocol == 17:
            self.mutator.log(f"UDP: {src_ip} → {dst_ip}")
        else:
            self.mutator.log(f"Other IP: {src_ip} → {dst_ip}")

# 🌐 GeoIP Mapper
class GeoIPMapper:
    def __init__(self, db_path="GeoLite2-City.mmdb", mutator=None):
        self.mutator = mutator
        try:
            self.reader = geoip2.database.Reader(db_path)
        except:
            self.reader = None
            self.mutator.log("GeoIP DB not found. Download from https://dev.maxmind.com/geoip/geolite2/")

    def map(self, ip):
        if not self.reader:
            return "Unknown"
        try:
            response = self.reader.city(ip)
            location = f"{response.city.name}, {response.country.name}"
            self.mutator.log(f"GeoIP: {ip} → {location}")
            return location
        except:
            return "Unknown"

# 🔐 Vault Engine
class VaultEngine:
    def __init__(self, ttl=90):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.store = {}
        self.ttl = ttl

    def save(self, label, data):
        encrypted = self.cipher.encrypt(data.encode())
        self.store[label] = (encrypted, time.time())

    def retrieve(self, label):
        if label in self.store:
            encrypted, timestamp = self.store[label]
            if time.time() - timestamp < self.ttl:
                return self.cipher.decrypt(encrypted).decode()
            else:
                del self.store[label]
        return None

    def purge(self):
        now = time.time()
        for label in list(self.store.keys()):
            _, timestamp = self.store[label]
            if now - timestamp >= self.ttl:
                del self.store[label]

# 🧠 Reasoning Engine
class ReasoningEngine:
    def __init__(self, target="magicbox_cloak_node.py", mutator=None):
        self.target = target
        self.mutator = mutator

    def scan_and_repair(self):
        try:
            with open(self.target, "r") as f:
                code = f.read()
            if "time.sleep(10)" in code:
                mutated = code.replace("time.sleep(10)", "time.sleep(5)")
                with open(self.target, "w") as f:
                    f.write(mutated)
                self.mutator.log("Self-healing: sleep(10) → sleep(5)")
        except Exception as e:
            self.mutator.log(f"Repair failed: {e}")

# 🌀 Swarm Dashboard
class SwarmDashboard:
    def __init__(self, mutator=None):
        self.nodes = {}
        self.mutator = mutator

    def register(self, ip):
        node_id = str(uuid.uuid4())
        self.nodes[node_id] = {"ip": ip, "timestamp": time.time()}
        self.mutator.log(f"Node registered: {node_id} → {ip}")

    def purge(self, ttl=120):
        now = time.time()
        for node_id in list(self.nodes.keys()):
            if now - self.nodes[node_id]["timestamp"] > ttl:
                del self.nodes[node_id]
                self.mutator.log(f"Node purged: {node_id}")

# 🎭 GUI Overlay (MagicBox Theme)
class GUIOverlay:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox Cloak Node")
        self.root.geometry("900x700")
        self.root.configure(bg="#0f0f1f")

        self.canvas = Canvas(self.root, width=900, height=400, bg="#0f0f1f", highlightthickness=0)
        self.canvas.pack()

        self.status = tk.Label(self.root, text="Status: Idle", fg="lime", bg="#0f0f1f", font=("Consolas", 14))
        self.status.pack(pady=10)

        self.log_box = tk.Text(self.root, height=10, bg="black", fg="cyan", font=("Consolas", 10))
        self.log_box.pack(fill="x", padx=10)

        self.particles = []
        self.animate_particles()

    def update_status(self, msg):
        self.status.config(text=f"Status: {msg}")
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)

    def animate_particles(self):
        for _ in range(30):
            x, y = uuid.uuid4().int % 900, uuid.uuid4().int % 400
            dot = self.canvas.create_oval(x, y, x+4, y+4, fill="cyan", outline="")
            self.particles.append(dot)
        self.move_particles()

    def move_particles(self):
        for dot in self.particles:
            dx, dy = uuid.uuid4().int % 3 - 1, uuid.uuid4().int % 3 - 1
            self.canvas.move(dot, dx, dy)
        self.root.after(100, self.move_particles)

    def run(self):
        self.root.mainloop()

# 🚀 Launch Everything
if __name__ == "__main__":
    gui = GUIOverlay()
    mutator = MutationHooks(gui)

    vault = VaultEngine()
    geoip = GeoIPMapper(mutator=mutator)
    reasoning = ReasoningEngine(mutator=mutator)
    dashboard = SwarmDashboard(mutator=mutator)
    sniffer = PacketSniffer(mutator=mutator)

    threading.Thread(target=sniffer.start, daemon=True).start()
    threading.Thread(target=lambda: [reasoning.scan_and_repair() or time.sleep(30)], daemon=True).start()
    threading.Thread(target=lambda: [dashboard.purge() or time.sleep(60)], daemon=True).start()

    vault.save("test", "Encrypted swarm seed")
    mutator.log(f"Vault test: {vault.retrieve('test')}")
    mutator.log(f"GeoIP test: 8.8.8.8 → {geoip.map('8.8.8.8')}")
    dashboard.register("192.168.1.101")

    gui.run()

