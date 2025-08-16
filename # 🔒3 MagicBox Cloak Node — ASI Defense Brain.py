# 🔒 MagicBox Cloak Node — ASI Defense Brain
import os, sys, threading, random, math, subprocess
from datetime import datetime, timedelta
import tkinter as tk
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 🧰 Auto-install required libraries
def ensure_libs():
    try:
        import dearpygui.dearpygui as dpg
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "dearpygui"])
    try:
        import watchdog
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "watchdog"])

ensure_libs()
import dearpygui.dearpygui as dpg

# 🧠 Memory & Ingestion
BIO_DATA_STORE = []
FAKE_TELEMETRY = []
NODE_SWARM = {}

def load_memory(): return {"history": []}
def save_memory(memory): pass
def get_current_timestamp(): return datetime.now().isoformat()
def generate_symbolic_trace(emotion, overlays, seed): return f"{emotion}:{seed}:{'-'.join(overlays)}"

def trigger_data_self_destruct(payload, delay=3):
    def destroy():
        payload.clear() if isinstance(payload, dict) else None
    threading.Timer(delay, destroy).start()

def zero_trust_check(identity):
    trusted_identities = {"system_core", "authorized_user"}
    if identity not in trusted_identities:
        raise PermissionError(f"Zero Trust blocked '{identity}'")

def store_bio_data(data):
    expiry = datetime.now() + timedelta(days=1)
    BIO_DATA_STORE.append({"data": data, "expires": expiry})

def purge_expired_bio_data():
    now = datetime.now()
    BIO_DATA_STORE[:] = [entry for entry in BIO_DATA_STORE if entry["expires"] > now]

def generate_fake_telemetry():
    fake = {
        "cpu": random.randint(1, 100),
        "location": "Null Island",
        "identity": "ghost-node",
        "timestamp": datetime.now()
    }
    FAKE_TELEMETRY.append(fake)
    threading.Timer(30, lambda: FAKE_TELEMETRY.remove(fake)).start()

# 🧠 Symbolic Ingestion
def emotion_resolver(filename):
    if "error" in filename.lower(): return "dread"
    elif "log" in filename.lower(): return "curiosity"
    elif "report" in filename.lower(): return "awe"
    return "neutral"

def overlay_generator(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ["glyph:spiral", "aura:blue"] if ext == ".txt" else ["glyph:burst", "aura:red"]

def add_ingestion_record(emotion, overlays, seed):
    memory = load_memory()
    record = {
        "timestamp": get_current_timestamp(),
        "emotion": emotion,
        "overlays": overlays,
        "seed": seed,
        "symbolic_trace": generate_symbolic_trace(emotion, overlays, seed)
    }
    memory.setdefault("history", []).append(record)
    save_memory(memory)
    NODE_SWARM[seed] = {"emotion": emotion, "overlays": overlays}
    return memory

class SymbolicIngestionHandler(FileSystemEventHandler):
    def __init__(self, watch_dir): self.watch_dir = watch_dir
    def on_created(self, event):
        if event.is_directory: return
        filename = os.path.basename(event.src_path)
        emotion = emotion_resolver(filename)
        overlays = overlay_generator(filename)
        add_ingestion_record(emotion, overlays, filename)

def ensure_watch_directory(path):
    if not os.path.exists(path): os.makedirs(path)

def ingest_existing_files(path):
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            emotion = emotion_resolver(filename)
            overlays = overlay_generator(filename)
            add_ingestion_record(emotion, overlays, filename)

def start_symbolic_watcher(watch_dir):
    handler = SymbolicIngestionHandler(watch_dir)
    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=False)
    observer.start()

# 🌌 GUI: Tkinter Neural Web Interface
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width: self.dx *= -1
        if self.y <= 0 or self.y >= height: self.dy *= -1

    def draw(self):
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#00F7FF", outline=""
        )

def launch_network_gui():
    root = tk.Tk()
    root.title("🧠 MagicBox Neural Web")
    root.geometry("720x520")
    root.configure(bg="#0B0E1A")

    canvas_width, canvas_height = 700, 460
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(40)]

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(canvas_width, canvas_height)
            node.draw()
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill="#00F7FF", width=1)
        root.after(30, animate)

    animate()
    root.mainloop()

# 🌐 DearPyGui Threat Map
def create_threat_map():
    with dpg.window(label="Mythic Threat Map", width=1000, height=700, pos=(50, 50)):
        with dpg.drawlist(width=1000, height=700, tag="threat_map"):
            dpg.draw_text((20, 20), "🗺️ Threat Map Activated", size=20, color=(255, 255, 255, 255))
        dpg.add_slider_float(label="Zoom", default_value=1.0, min_value=0.5, max_value=2.0,
                             callback=lambda s, a: dpg.set_item_scale("threat_map", a))
        dpg.add_slider_float(label="Pan X", default_value=0, min_value=-500, max_value=500,
                             callback=lambda s, a: dpg.set_item_pos("threat_map", (a, dpg.get_item_pos("threat_map")[1])))
        dpg.add_slider_float(label="Pan Y", default_value=0, min_value=-500, max_value=500,
                             callback=lambda s, a: dpg.set_item_pos("threat_map", (dpg.get_item_pos("threat_map")[0], a)))

def update_threat_density():
    emotion_count = {"dread": 0, "curiosity": 0, "awe": 0, "neutral": 0}
    for node in NODE_SWARM.values():
        emotion_count[node["emotion"]] += 1
    print("📊 Threat Density:", emotion_count)
    threading.Timer(10, update_threat_density).start()

# 🧠 ASI Self-Evolving Logic
def evolve_defense_brain():
    print("🧠 ASI Brain evolving...")
    # Placeholder for future code rewriting logic
    threading.Timer(60, evolve_defense_brain).start()

# 🚀 Launch Everything
def launch_firewall_hud(watch_directory="./ingest_zone"):
    ensure_watch_directory(watch_directory)
    ingest_existing_files(watch_directory)
    start_symbolic_watcher(watch_directory)
    threading.Thread(target=launch_network_gui, daemon=True).start()
    dpg.create_context()
    create_threat_map()
    dpg.create_viewport(title='Mythic Firewall HUD', width=1200, height=800)

    dpg.setup_dearpygui()
    update_threat_density()
    evolve_defense_brain()  # 🔁 Begin ASI self-evolution loop
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

# 🔥 Activate Everything
if __name__ == "__main__":
    try:
        zero_trust_check("authorized_user")  # ✅ Identity verification
        generate_fake_telemetry()            # 🕵️ Cloaking layer
        purge_expired_bio_data()             # 🧼 Vault hygiene
        launch_firewall_hud()                # 🚀 Full system launch
    except PermissionError as e:
        print(f"🚫 Access Denied: {e}")

