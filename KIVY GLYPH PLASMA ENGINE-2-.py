# ━━━━━━━━━━━━━━━━ AUTOLOADER ━━━━━━━━━━━━━━━━
import subprocess, sys

def ensure_package(pkg, alias=None):
    try:
        __import__(alias or pkg)
    except ImportError:
        print(f"📦 Installing missing package: {pkg}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        __import__(alias or pkg)

REQUIRED_PACKAGES = [
    ("tkinter", "tkinter"),
    ("psutil", "psutil"),
    ("kivy", "kivy"),
    ("numpy", "numpy")
]

for pkg, alias in REQUIRED_PACKAGES:
    ensure_package(pkg, alias)

# ━━━━━━━━━━━━━━━━ PREFLIGHT CHECKS ━━━━━━━━━━━━━━━━
import os, platform, socket, math, time, random, hashlib

REQUIRED_FONT = "Orbitron"
REQUIRED_OS = ["Windows", "Linux", "Darwin"]

def verify_environment():
    current_os = platform.system()
    if current_os not in REQUIRED_OS:
        print(f"❌ Unsupported OS: {current_os}")
        sys.exit(1)
    else:
        print(f"✅ OS verified: {current_os}")

def font_check():
    try:
        import tkinter as tk
        import tkinter.font as tkFont
        root = tk.Tk()
        fonts = tkFont.families()
        root.destroy()
        if REQUIRED_FONT not in fonts:
            print(f"⚠️ Font '{REQUIRED_FONT}' not found.")
        else:
            print(f"✅ Font '{REQUIRED_FONT}' available.")
    except Exception as e:
        print(f"⚠️ Font check failed: {e}")

def run_preflight():
    print("\n🧠 OVERMIND PREFLIGHT INITIATED\n")
    verify_environment()
    font_check()
    print("⚡ Integrity check complete. Preparing Overmind...\n")

run_preflight()

# ━━━━━━━━━━━━━━━━ SYSTEM HOOKS ━━━━━━━━━━━━━━━━
import psutil
import tkinter as tk
from tkinter import ttk
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window

def fetch_persona_state():
    system = platform.system()
    hostname = socket.gethostname()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    if cpu < 30 and ram < 50:
        mood = "Calm"
    elif cpu < 65:
        mood = "Alert"
    elif cpu < 90:
        mood = "Hostile"
    else:
        mood = "Transcendent"

    glyph = "🖥️" if system == "Windows" else "🧬"
    return {"name": hostname, "mood": mood, "glyph": glyph}

def fetch_threat_level():
    cpu = psutil.cpu_percent()
    disk = psutil.disk_usage('/').percent
    net = psutil.net_io_counters().packets_sent
    if cpu > 90 or disk > 90:
        return "Critical"
    elif cpu > 70 or net > 50000:
        return "Elevated"
    elif cpu > 40:
        return "Low"
    else:
        return "None"

def fetch_emotional_color(mood):
    return {
        "Calm": "#5DADE2",
        "Alert": "#F4D03F",
        "Hostile": "#E74C3C",
        "Transcendent": "#9B59B6"
    }.get(mood, "#2C3E50")

# ━━━━━━━━━━━━━━━━ TKINTER GUI ━━━━━━━━━━━━━━━━
class OvermindTkGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Overmind: Genesis Core")
        self.geometry("800x600")
        self.configure(bg="#1C1C1C")
        self.setup_styles()
        self.create_panels()
        self.refresh_data()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Overmind.TLabelframe", background="#1C1C1C", foreground="white")
        style.configure("Overmind.TLabelframe.Label", foreground="cyan", font=(REQUIRED_FONT, 12))

    def create_panels(self):
        self.persona_frame = ttk.LabelFrame(self, text="Active Persona", style="Overmind.TLabelframe")
        self.persona_frame.pack(padx=10, pady=10, fill="x")
        self.persona_label = tk.Label(self.persona_frame, text="", font=(REQUIRED_FONT, 20), fg="white", bg="#1C1C1C")
        self.persona_label.pack()

        self.canvas_frame = ttk.LabelFrame(self, text="Neural Canvas", style="Overmind.TLabelframe")
        self.canvas_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, bg="#2C3E50")
        self.canvas.pack(fill="both", expand=True)

        self.threat_frame = ttk.LabelFrame(self, text="Threat Assessment", style="Overmind.TLabelframe")
        self.threat_frame.pack(padx=10, pady=10, fill="x")
        self.threat_label = tk.Label(self.threat_frame, text="", font=(REQUIRED_FONT, 16), fg="white", bg="#1C1C1C")
        self.threat_label.pack()

    def refresh_data(self):
        persona = fetch_persona_state()
        threat = fetch_threat_level()
        mood_color = fetch_emotional_color(persona["mood"])

        self.persona_label.config(text=f"{persona['glyph']} {persona['name']} – {persona['mood']}")
        self.threat_label.config(text=f"Threat Level: {threat}")
        self.canvas.config(bg=mood_color)
        self.canvas.delete("all")
        self.after(2500, self.refresh_data)

# ━━━━━━━━━━━━━━━━ KIVY GLYPH PLASMA ENGINE ━━━━━━━━━━━━━━━━
class PlasmaGlyph:
    def __init__(self, center, radius, speed, color):
        self.angle = random.uniform(0, 360)
        self.radius = radius
        self.speed = speed
        self.center = center
        self.color = color
        self.history = []

    def update(self):
        self.angle += self.speed
        rad = math.radians(self.angle)
        x = self.center[0] + self.radius * math.cos(rad)
        y = self.center[1] + self.radius * math.sin(rad)
        self.history.append((x, y))
        if len(self.history) > 20:
            self.history.pop(0)
        return x, y

class AuraCanvas(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.glyphs = []
        Clock.schedule_once(self.init_glyphs, 0)
        Clock.schedule_interval(self.update_canvas, 1/30)

    def init_glyphs(self, *args):
        persona = fetch_persona_state()
        mood_color = fetch_emotional_color(persona["mood"])
        r, g, b = tuple(int(mood_color.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))
        center = (self.width / 2, self.height / 2)
        for _ in range(6):
            glyph = PlasmaGlyph(center=center, radius=random.randint(80, 200),
                                speed=random.uniform(1, 3), color=(r, g, b))
            self.glyphs.append(glyph)

    def update_canvas(self, dt):  # ✅ Accepts dt from Clock
        self.canvas.clear()
        persona = fetch_persona_state()
        mood_color = fetch_emotional_color(persona["mood"])
        r, g, b = tuple(int(mood_color.lstrip('#')[i:i+2], 16)/255 for i in (0, 2, 4))

        with self.canvas:
            Color(r, g, b, 0.2)
            Ellipse(pos=(self.width/2 - 10, self.height/2 - 10), size=(20, 20))

            for glyph in self.glyphs:
                x, y = glyph.update()
                Color(*glyph.color, 0.9)
                Ellipse(pos=(x - 8, y - 8), size=(16, 16))

                for i in range(len(glyph.history) - 1):
                    x1, y1 = glyph.history[i]
                    x2, y2 = glyph.history[i + 1]
                    fade = i / len(glyph.history)
                    Color(r, g, b, 0.3 * fade)
                    Line(points=[x1, y1, x2, y2], width=1.5)

class OvermindKivyApp(App):
    def build(self):
        Window.clearcolor = (0.1, 0.1, 0.1, 1)
        layout = BoxLayout(orientation='vertical')
        self.label = Label(text="Initializing Overmind...", font_size=24)
        self.canvas_widget = AuraCanvas()
        layout.add_widget(self.label)
        layout.add_widget(self.canvas_widget)
        Clock.schedule_interval(self.update_gui, 2.5)
        return layout

    def update_gui(self, dt):
        persona = fetch_persona_state()
        threat = fetch_threat_level()
        self.label.text = f"{persona['glyph']} {persona['name']} – {persona['mood']} | Threat: {threat}"
        self.canvas_widget.update_canvas(dt)

# ━━━━━━━━━━━━━━━━ IGNITION ━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    import threading
    threading.Thread(target=lambda: OvermindTkGUI().mainloop()).start()
    OvermindKivyApp().run()

