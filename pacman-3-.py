import sys
import subprocess
import importlib
import os
import random
import threading
from datetime import datetime, timedelta

# 🧰 Auto-install required libraries
REQUIRED_LIBS = {
    "dearpygui.dearpygui": "dearpygui",
    "watchdog": "watchdog"
}

def ensure_libs():
    missing = []
    for module_path, pip_name in REQUIRED_LIBS.items():
        try:
            importlib.import_module(module_path)
        except ImportError:
            missing.append(pip_name)

    if missing:
        print(f"🔧 Installing missing libraries: {', '.join(missing)}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", *missing])
        print("✅ Installation complete.")

ensure_libs()

# ✅ Safe to import now
import dearpygui.dearpygui as dpg
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

# 🧠 Memory management
def load_memory():
    return {"history": []}

def save_memory(memory):
    pass

def get_current_timestamp():
    return datetime.now().isoformat()

def generate_symbolic_trace(emotion, overlays, seed):
    return f"{emotion}:{seed}:{'-'.join(overlays)}"

GLYPH_EVENTS = {
    "self_destruct": {"glyph": "💣", "color": (255, 0, 0, 255), "ttl": 3},
    "trust_block": {"glyph": "🛡️", "color": (0, 200, 255, 255), "ttl": 5},
    "bio_purge": {"glyph": "🔥", "color": (255, 165, 0, 255), "ttl": 86400},
    "telemetry_purge": {"glyph": "🛰️", "color": (180, 180, 180, 255), "ttl": 30},
    "ingestion": {"glyph": "🌌", "color": (100, 255, 100, 255), "ttl": 10}
}

NODE_SWARM = {}

def create_progress_theme(color):
    theme_id = f"theme_{random.randint(1000,9999)}"
    with dpg.theme(tag=theme_id):
        with dpg.theme_component(dpg.mvProgressBar):
            dpg.add_theme_color(dpg.mvThemeCol_PlotHistogram, color)
    return theme_id

def apply_fusion_aura(node_id, color=(255, 255, 0, 255)):
    theme_id = f"fusion_theme_{random.randint(1000,9999)}"
    with dpg.theme(tag=theme_id):
        with dpg.theme_component(dpg.mvAll):
            dpg.add_theme_color(dpg.mvThemeCol_Border, color)
            dpg.add_theme_style(dpg.mvStyleVar_FrameBorderSize, 2)
    dpg.bind_item_theme(node_id, theme_id)

def trigger_particle_burst(center, count=10):
    for _ in range(count):
        offset = (random.randint(-30, 30), random.randint(-30, 30))
        pos = (center[0] + offset[0], center[1] + offset[1])
        dpg.draw_circle(center=pos, radius=3, color=(255, 255, 0, 200), fill=(255, 255, 0, 200), parent="threat_map")

def draw_node_trail(start_pos, end_pos, color=(255, 255, 255, 100)):
    dpg.draw_line(p1=start_pos, p2=end_pos, color=color, thickness=2, parent="threat_map")

def draw_heat_zone(center, emotion):
    color_map = {
        "dread": (255, 0, 0, 80),
        "curiosity": (0, 255, 255, 80),
        "awe": (255, 255, 0, 80),
        "neutral": (200, 200, 200, 50)
    }
    color = color_map.get(emotion, (255, 255, 255, 50))
    dpg.draw_circle(center=center, radius=60, color=color, fill=color, parent="threat_map")

def get_cluster_position(event_type, emotion):
    base_x = {"self_destruct": 100, "trust_block": 300, "bio_purge": 500, "telemetry_purge": 700, "ingestion": 400}.get(event_type, 400)
    base_y = {"dread": 100, "curiosity": 300, "awe": 500, "neutral": 400}.get(emotion, 400)
    return (base_x + random.randint(-30, 30), base_y + random.randint(-30, 30))

def register_node(node_id, event_type, emotion, overlays, created_at):
    NODE_SWARM[node_id] = {
        "event_type": event_type,
        "emotion": emotion,
        "overlays": overlays,
        "created_at": created_at,
        "mutated": False,
        "fused": False
    }

def mutate_node(node_id):
    node = NODE_SWARM.get(node_id)
    if not node or node["mutated"]:
        return
    node["mutated"] = True
    morph_map = {
        "dread": "💀",
        "curiosity": "🔍",
        "awe": "🌟",
        "neutral": "⚪"
    }
    new_glyph = morph_map.get(node["emotion"], "🔄")
    dpg.set_value(node_id + "_text", f"{new_glyph} Morphed from {node['event_type']}")

def trigger_contagion(source_id):
    source = NODE_SWARM.get(source_id)
    if not source:
        return
    for target_id, target in NODE_SWARM.items():
        if target_id != source_id and not target["mutated"]:
            mutate_node(target_id)
            draw_node_trail(dpg.get_item_pos(source_id), dpg.get_item_pos(target_id), (255, 0, 255, 150))

def try_fusion():
    clusters = {}
    for node_id, node in NODE_SWARM.items():
        key = node["event_type"]
        clusters.setdefault(key, []).append(node_id)
    for event_type, ids in clusters.items():
        if len(ids) >= 3:
            for nid in ids:
                dpg.set_value(nid + "_text", f"⚛️ Fused {event_type}")
                NODE_SWARM[nid]["fused"] = True
                apply_fusion_aura(nid)
                trigger_particle_burst(dpg.get_item_pos(nid))

def spawn_glyph_node(event_type, message, emotion="neutral", overlays=None):
    config = GLYPH_EVENTS.get(event_type)
    if not config:
        return
    glyph = config["glyph"]
    color = config["color"]
    ttl = config["ttl"]
    node_id = f"{event_type}_{random.randint(1000, 9999)}"
    pos = get_cluster_position(event_type, emotion)

    with dpg.window(label=node_id, width=250, height=80, pos=pos,
                    no_close=True, no_resize=True, no_move=True, no_title_bar=True):
        text_id = dpg.add_text(f"{glyph} {message}", tag=node_id + "_text", color=(255, 255, 255, 255))
        dpg.add_spacer(height=5)
        bar_id = dpg.add_progress_bar(default_value=1.0, overlay="Security Pulse")
        theme = create_progress_theme(color)
        dpg.bind_item_theme(bar_id, theme)

    register_node(node_id, event_type, emotion, overlays, datetime.now())
    draw_heat_zone(pos, emotion)

    threading.Timer(ttl, lambda: dpg.delete_item(node_id)).start()
    threading.Timer(ttl / 2, lambda: mutate_node(node_id)).start()
    threading.Timer(ttl / 3, lambda: trigger_contagion(node_id)).start()
    threading.Timer(ttl / 4, try_fusion).start()

# 🛡️ Security Modules
def trigger_data_self_destruct(payload, delay=3):
    def destroy():
        spawn_glyph_node("self_destruct", "Unauthorized data exfiltration")
        payload.clear() if isinstance(payload, dict) else None
    threading.Timer(delay, destroy).start()

def zero_trust_check(identity):
    trusted_identities = {"system_core", "authorized_user"}
    if identity not in trusted_identities:
        spawn_glyph_node("trust_block", f"Blocked '{identity}'")
        raise PermissionError("Zero Trust Sentinel blocked access.")

BIO_DATA_STORE = []

def store_bio_data(data):
    expiry = datetime.now() + timedelta(days=1)
    BIO_DATA_STORE.append({"data": data, "expires": expiry})
    spawn_glyph_node("bio_purge", "Bio-data stored with 1-day TTL")

def purge_expired_bio_data():
    now = datetime.now()
    BIO_DATA_STORE[:] = [entry for entry in BIO_DATA_STORE if entry["expires"] > now]

FAKE_TELEMETRY = []

def generate_fake_telemetry():
    fake = {
        "cpu": random.randint(1, 100),
        "location": "Null Island",
        "identity": "ghost-node",
        "timestamp": datetime.now()
    }
    FAKE_TELEMETRY.append(fake)
    spawn_glyph_node("telemetry_purge", "Fake telemetry dispatched")
    threading.Timer(30, lambda: FAKE_TELEMETRY.remove(fake)).start()

# 🧠 Emotion and Overlay Mapping
def emotion_resolver(filename):
    if "error" in filename.lower():
        return "dread"
    elif "log" in filename.lower():
        return "curiosity"
    elif "report" in filename.lower():
        return "awe"
    return "neutral"

def overlay_generator(filename):
    ext = os.path.splitext(filename)[1].lower()
    return ["glyph:spiral", "aura:blue"] if ext == ".txt" else ["glyph:burst", "aura:red"]

# 🧠 Ingestion Record
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
    spawn_glyph_node("ingestion", f"Ingested '{seed}'", emotion=emotion, overlays=overlays)
    return memory

# 🧠 Symbolic Ingestion Trigger
class SymbolicIngestionHandler(FileSystemEventHandler):
    def __init__(self, watch_dir, emotion_resolver, overlay_generator):
        self.watch_dir = watch_dir
        self.emotion_resolver = emotion_resolver
        self.overlay_generator = overlay_generator

    def on_created(self, event):
        if event.is_directory:
            return
        filepath = event.src_path
        filename = os.path.basename(filepath)
        seed = filename
        emotion = self.emotion_resolver(filename)
        overlays = self.overlay_generator(filename)
        add_ingestion_record(emotion, overlays, seed)

# 🧱 Ensure Watch Directory Exists
def ensure_watch_directory(path):
    if not os.path.exists(path):
        os.makedirs(path)
        spawn_glyph_node("ingestion", f"Created watch directory: {path}")

# 🔁 Auto-ingest existing files
def ingest_existing_files(path):
    for filename in os.listdir(path):
        full_path = os.path.join(path, filename)
        if os.path.isfile(full_path):
            emotion = emotion_resolver(filename)
            overlays = overlay_generator(filename)
            add_ingestion_record(emotion, overlays, filename)

# 🚀 Launch the observer
def start_symbolic_watcher(watch_dir):
    handler = SymbolicIngestionHandler(watch_dir, emotion_resolver, overlay_generator)
    observer = Observer()
    observer.schedule(handler, watch_dir, recursive=False)
    observer.start()
    spawn_glyph_node("ingestion", f"Watching '{watch_dir}' for mythic events")

# 🗺️ Create Threat Map Canvas
def create_threat_map():
    with dpg.window(label="Mythic Threat Map", width=1000, height=700, pos=(50, 50)):
        with dpg.drawlist(width=1000, height=700, tag="threat_map"):
            dpg.draw_text((20, 20), "🗺️ Threat Map Activated", size=20, color=(255, 255, 255, 255))
        dpg.add_slider_float(label="Zoom", default_value=1.0, min_value=0.5, max_value=2.0, callback=update_zoom)
        dpg.add_slider_float(label="Pan X", default_value=0, min_value=-500, max_value=500, callback=update_pan_x)
        dpg.add_slider_float(label="Pan Y", default_value=0, min_value=-500, max_value=500, callback=update_pan_y)

def update_zoom(sender, app_data):
    dpg.set_item_scale("threat_map", app_data)

def update_pan_x(sender, app_data):
    dpg.set_item_pos("threat_map", (app_data, dpg.get_item_pos("threat_map")[1]))

def update_pan_y(sender, app_data):
    dpg.set_item_pos("threat_map", (dpg.get_item_pos("threat_map")[0], app_data))

# 📊 Threat Density Analytics
def update_threat_density():
    emotion_count = {"dread": 0, "curiosity": 0, "awe": 0, "neutral": 0}
    for node in NODE_SWARM.values():
        emotion = node["emotion"]
        emotion_count[emotion] += 1
    print("📊 Threat Density:", emotion_count)
    threading.Timer(10, update_threat_density).start()

# 🌀 Launch HUD and Watcher
def launch_firewall_hud(watch_directory="./ingest_zone"):
    ensure_watch_directory(watch_directory)
    ingest_existing_files(watch_directory)
    dpg.create_context()
    create_threat_map()
    dpg.create_viewport(title='Mythic Firewall HUD', width=1200, height=800)
    dpg.setup_dearpygui()
    start_symbolic_watcher(watch_directory)
    update_threat_density()
    dpg.show_viewport()
    dpg.start_dearpygui()
    dpg.destroy_context()

# 🔥 Start the mythic system
launch_firewall_hud()

