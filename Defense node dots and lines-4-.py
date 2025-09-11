# 🧰 Auto-loader
import subprocess, sys
def ensure_libs():
    try:
        import tkinter, pyttsx3, random, math, threading, time, os, queue
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyttsx3"])
ensure_libs()

# 🔊 Voice Engine Setup (Thread-Safe)
import pyttsx3, threading, time, tkinter as tk, random, math, queue

engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

voice_queue = queue.Queue()

def voice_worker():
    while True:
        msg = voice_queue.get()
        if msg:
            engine.say(msg)
            engine.runAndWait()
        voice_queue.task_done()

threading.Thread(target=voice_worker, daemon=True).start()

# 📜 Symbolic Feedback
def symbolic_log(message):
    print(f"[📜] {message}")
    voice_queue.put(message)

# 🔒 Threat Matrix
class ThreatMatrix:
    def __init__(self):
        self.threats = []

    def ingest(self, data_type, origin="unknown"):
        timestamp = time.time()
        self.threats.append({"type": data_type, "origin": origin, "timestamp": timestamp})
        symbolic_log(f"Ingested {data_type} from {origin}")

    def purge_expired(self, codex):
        now = time.time()
        before = len(self.threats)
        self.threats = [t for t in self.threats if now - t["timestamp"] < codex.get_retention(t["type"])]
        after = len(self.threats)
        if before != after:
            symbolic_log(f"Purged {before - after} expired threats")

# 🧬 Codex with Ancestry Tracking
class Codex:
    def __init__(self):
        self.rules = {
            "Telemetry": 30,
            "MAC/IP": 30,
            "Backdoor Data": 3,
            "Personal Data": 86400
        }
        self.ancestry = []

    def get_retention(self, data_type):
        return self.rules.get(data_type, 60)

    def mutate(self, trigger):
        if trigger == "ghost_sync":
            old = self.rules["Telemetry"]
            self.rules["Telemetry"] = max(10, old - 10)
            mutation = {
                "trigger": trigger,
                "change": f"Telemetry {old} → {self.rules['Telemetry']}",
                "timestamp": time.time()
            }
            self.ancestry.append(mutation)
            symbolic_log(f"Codex mutated: {mutation['change']}")
            return "phantom_node"

# 🎭 Persona Injection & Rotation
class Persona:
    def __init__(self, name):
        self.name = name
        self.active = True

    def narrate(self):
        symbolic_log(f"Persona {self.name} deployed into the mythic veil")

class PersonaSwarm:
    def __init__(self, personas):
        self.personas = personas
        self.index = 0

    def rotate(self):
        self.index = (self.index + 1) % len(self.personas)
        active = self.personas[self.index]
        symbolic_log(f"Persona rotated: {active.name}")
        return active

# 🌐 Country Filter
class CountryFilter:
    def __init__(self):
        self.allowed = {"US", "CA", "UK"}

    def is_allowed(self, origin):
        return origin in self.allowed

# 🧿 Holographic Pulse Simulation
def holographic_pulse(canvas, width, height):
    for _ in range(5):
        x, y = random.randint(0, width), random.randint(0, height)
        r = random.randint(10, 30)
        canvas.create_oval(x-r, y-r, x+r, y+r, outline="#FF00FF", width=2)

# 🧠 Node Class
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

# 🖥️ GUI Launcher
def launch_guardian_gui(threat_matrix, codex, persona_swarm, country_filter):
    root = tk.Tk()
    root.title("🧠 The Guardian — MythicNode Defense")
    root.geometry("800x600")
    root.configure(bg="#0B0E1A")

    canvas = tk.Canvas(root, width=780, height=540, bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    nodes = [Node(canvas, 780, 540) for _ in range(40)]

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(780, 540)
            node.draw()
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill="#00F7FF", width=1)
        holographic_pulse(canvas, 780, 540)
        root.after(30, animate)

    persona_swarm.rotate().narrate()
    animate()
    root.mainloop()

# 🛡️ Daemon Logic
def guardian_daemon(threat_matrix, codex, country_filter):
    symbolic_log("Guardian Daemon running silently in background...")
    threat_matrix.ingest("MAC/IP", "US")
    threat_matrix.ingest("Backdoor Data", "RU")
    threat_matrix.ingest("Personal Data", "CA")

    if not country_filter.is_allowed("RU"):
        symbolic_log("Blocked data from RU")

    ghost = codex.mutate("ghost_sync")
    threat_matrix.ingest("Telemetry", "phantom")
    threat_matrix.purge_expired(codex)

# 🔐 Encrypted Swarm Sync
def encrypted_swarm_sync(codex_list):
    symbolic_log("Encrypted swarm sync initiated...")
    merged_rules = {}
    for codex in codex_list:
        for k, v in codex.rules.items():
            merged_rules[k] = min(merged_rules.get(k, v), v)
    symbolic_log(f"Swarm codex merged: {merged_rules}")
    return merged_rules

# 🧙 MagicBox Launcher
def magicbox():
    threat_matrix = ThreatMatrix()
    codex = Codex()
    country_filter = CountryFilter()
    personas = [Persona("ThreatHunter"), Persona("Compliance Auditor"), Persona("GhostWalker")]
    persona_swarm = PersonaSwarm(personas)

    threading.Thread(target=guardian_daemon, args=(threat_matrix, codex, country_filter)).start()
    threading.Thread(target=lambda: encrypted_swarm_sync([codex])).start()
    launch_guardian_gui(threat_matrix, codex, persona_swarm, country_filter)

# 🧓 One-Click Entry Point
if __name__ == "__main__":
    symbolic_log("Launching MagicBox Edition — Old Guy Friendly Mode")
    magicbox()

