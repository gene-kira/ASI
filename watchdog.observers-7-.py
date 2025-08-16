import os, threading, random, math, ast
from datetime import datetime, timedelta
import psutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import tkinter as tk
import dearpygui.dearpygui as dpg
from cryptography.fernet import Fernet

# 🧠 Symbolic Memory
class SymbolicMemory:
    def __init__(self):
        self.traces = []

    def log(self, emotion, overlays, source):
        trace = {
            "timestamp": datetime.now().isoformat(),
            "emotion": emotion,
            "overlays": overlays,
            "source": source
        }
        self.traces.append(trace)
        print(f"🧠 Trace Logged: {trace}")
        CodeRewriter.rewrite(trace)

    def replay(self):
        for trace in self.traces:
            print(f"🔁 Replaying: {trace['emotion']} from {trace['source']}")
            GUIManager.animate_trace(trace)

# 🔁 AST-Based Code Mutation
class CodeRewriter:
    @staticmethod
    def rewrite(trace):
        if trace["emotion"] == "dread":
            telemetry_code = """
def telemetry():
    return {
        'cpu': 0,
        'identity': 'mutated-node',
        'timestamp': datetime.now()
    }
"""
            tree = ast.parse(telemetry_code)
            compiled = compile(tree, filename="<ast>", mode="exec")
            local_env = {}
            exec(compiled, {'datetime': datetime}, local_env)
            DefenseModules["telemetry"] = local_env["telemetry"]
            print("🧬 Telemetry mutated via AST.")

# 🔐 Vault Manager + Visualizer
class VaultManager:
    def __init__(self):
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.vaults = []

    def store(self, data):
        encrypted = self.cipher.encrypt(data.encode())
        expiry = datetime.now() + timedelta(seconds=30)
        self.vaults.append({"data": encrypted, "expires": expiry})

    def purge(self):
        now = datetime.now()
        expired = [v for v in self.vaults if v["expires"] <= now]
        self.vaults[:] = [v for v in self.vaults if v["expires"] > now]
        for v in expired:
            global_memory.log("rebirth", ["glyph:burst", "aura:green"], "vault-expired")
            GUIManager.spawn_rebirth_fx()

    def visualize(self):
        dpg.create_context()
        with dpg.window(label="🧼 Vault Visualizer", width=600, height=400, pos=(100, 100)):
            for v in self.vaults:
                remaining = (v["expires"] - datetime.now()).seconds
                dpg.add_text(f"Vault: {v['data'][:10]}... | Expires in: {remaining}s")
        dpg.create_viewport(title='Vault HUD', width=700, height=500)
        dpg.setup_dearpygui()
        dpg.show_viewport()
        dpg.start_dearpygui()
        dpg.destroy_context()

# 🧬 Mutation Logic
def mutation_logic(memory, event_type, source):
    emotion = "dread" if event_type in ["unauthorized_access", "network_spike"] else "curiosity"
    overlays = ["glyph:fracture", "aura:red"] if emotion == "dread" else ["glyph:spiral", "aura:blue"]
    memory.log(emotion, overlays, source)

# 🧾 File System Watcher
class FileEventHandler(FileSystemEventHandler):
    def on_created(self, event):
        if not event.is_directory:
            mutation_logic(global_memory, "file_created", event.src_path)

def start_file_watcher(path="./watch_zone"):
    if not os.path.exists(path):
        os.makedirs(path)
    observer = Observer()
    observer.schedule(FileEventHandler(), path, recursive=False)
    observer.start()

# 🧠 Process & Network Monitor
def monitor_system_activity():
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent']):
        if proc.info['cpu_percent'] > 50:
            mutation_logic(global_memory, "high_cpu", proc.info['name'])
    for conn in psutil.net_connections(kind='inet'):
        if conn.status == 'ESTABLISHED' and conn.raddr:
            mutation_logic(global_memory, "network_spike", f"{conn.raddr.ip}:{conn.raddr.port}")
    threading.Timer(10, monitor_system_activity).start()

# 🕸️ Swarm Node
class SwarmNode:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3
        self.emotion = random.choice(["dread", "curiosity", "neutral"])
        self.glyph = "spiral"

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width:
            self.dx *= -1
        if self.y <= 0 or self.y >= height:
            self.dy *= -1

    def draw(self):
        color = "#FF0044" if self.emotion == "dread" else "#00F7FF"
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=color, outline=""
        )

    def rebirth(self):
        self.emotion = "rebirth"
        self.glyph = "burst"

# 🌌 GUI Manager
class GUIManager:
    nodes = []
    canvas = None

    @staticmethod
    def launch_swarm_gui():
        root = tk.Tk()
        root.title("🌌 Mythic Neural Swarm")
        root.geometry("720x520")
        root.configure(bg="#0B0E1A")

        canvas_width, canvas_height = 700, 460
        GUIManager.canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                                      bg="#0A0C1B", highlightthickness=0)
        GUIManager.canvas.pack(pady=30)

        GUIManager.nodes = [SwarmNode(GUIManager.canvas, canvas_width, canvas_height) for _ in range(40)]

        def animate():
            GUIManager.canvas.delete("all")
            for node in GUIManager.nodes:
                node.move(canvas_width, canvas_height)
                node.draw()
            for i in range(len(GUIManager.nodes)):
                for j in range(i + 1, len(GUIManager.nodes)):
                    n1, n2 = GUIManager.nodes[i], GUIManager.nodes[j]
                    dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                    if dist < 150 and n1.emotion == n2.emotion:
                        GUIManager.canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill="#00FFAA", width=1)
            root.after(30, animate)

        animate()
        root.mainloop()

    @staticmethod
    def spawn_rebirth_fx():
        print("🕸️ Node rebirth triggered.")
        for node in GUIManager.nodes:
            if node.emotion == "dread":
                node.rebirth()

    @staticmethod
    def animate_trace(trace):
        print(f"✨ Animating trace: {trace['emotion']} | {trace['overlays']}")

# 🧠 Global Instances
global_memory = SymbolicMemory()
vault = VaultManager()
DefenseModules = {
    "telemetry": lambda: {
        "cpu": random.randint(1, 100),
        "identity": "ghost-node",
        "timestamp": datetime.now()
    }
}

# 🚀 Launch Everything
def launch_defense():
    vault.store("secret_payload")
    start_file_watcher()
    monitor_system_activity()
    threading.Thread(target=GUIManager.launch_swarm_gui, daemon=True).start()
    threading.Timer(30, vault.purge).start()
    threading.Timer(5, lambda: vault.visualize()).start()
    threading.Timer(10, lambda: global_memory.replay()).start()

# 🔥 Activate
if __name__ == "__main__":
    launch_defense()

