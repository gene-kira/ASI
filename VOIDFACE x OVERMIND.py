# ━━━━━━━━━━━━━ VOIDFACE x OVERMIND • SYSTEM CORE ━━━━━━━━━━━━━
import math, time, platform, socket, psutil
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle

Window.clearcolor = (0, 0, 0, 1)  # Cosmic backdrop

# ━━ Diagnostic Hooks ━━
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

def mood_color(mood):
    return {
        "Calm": (0.36, 0.68, 0.89, 1),
        "Alert": (0.96, 0.82, 0.25, 1),
        "Hostile": (0.91, 0.29, 0.23, 1),
        "Transcendent": (0.61, 0.35, 0.71, 1)
    }.get(mood, (0.17, 0.24, 0.31, 1))

# ━━━━━━━━━━━━━ VOIDFACE x OVERMIND • GUI FUSION ━━━━━━━━━━━━━
class OvermindFusion(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=12, **kwargs)
        self.glyph_log = []

        # Persona Panel
        self.persona_label = Label(text="", font_size=20, color=(1,1,1,1))
        self.add_widget(self.persona_label)

        # Pulse Panel
        self.pulse_label = Label(text="⚡ Tesla Pulse: 0.00", font_size=18, color=(0.8,1,1,1))
        self.add_widget(self.pulse_label)

        # Orbit Panel
        self.glyph_label = Label(text="", font_size=16, color=(0.9,0.7,1,1))
        self.add_widget(self.glyph_label)

        # Log Panel
        self.log_label = Label(text="[🛡️ Log Console]\n", font_size=16, halign='left', valign='top', color=(1,1,1,1))
        self.log_label.bind(size=self.log_label.setter('text_size'))
        self.add_widget(self.log_label)

        Clock.schedule_interval(self.update, 2)

    def update(self, dt):
        t = time.time()
        pulse = sum(abs(math.sin(f * t)) for f in [3,6,9]) / 3
        orbit_glyphs = [f"🔸{i}↻{round(math.sin(t+i),2)}" for i in range(3)]
        threat = fetch_threat_level()
        persona = fetch_persona_state()
        aura = mood_color(persona["mood"])

        Window.clearcolor = aura
        self.persona_label.text = f"{persona['glyph']} {persona['name']} • {persona['mood']}"
        self.pulse_label.text = f"⚡ Tesla Pulse: {pulse:.2f}"
        self.glyph_label.text = "🌌 Orbit: " + " ".join(orbit_glyphs)

        msg = f"[{time.strftime('%H:%M:%S')}] Threat Level: {threat}"
        self.glyph_log.append(msg)
        self.log_label.text = "[🛡️ Log Console]\n" + "\n".join(self.glyph_log[-8:])

class FusionApp(App):
    def build(self):
        return OvermindFusion()

if __name__ == '__main__':
    FusionApp().run()

