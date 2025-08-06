# AutoLoader
import subprocess, sys
for pkg in [("kivy",), ("numpy",)]:
    try: __import__(pkg[0])
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg[0]])

# Imports
import math, random, time, hashlib, json, os
import numpy as np
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, InstructionGroup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Harmonics
class HarmonicResonator:
    def __init__(self): self.f3, self.f6, self.f9 = 3, 6, 9
    def pulse(self, t): return {
        '3': round(math.sin(self.f3 * t), 3),
        '6': round(math.sin(self.f6 * t), 3),
        '9': round(math.sin(self.f9 * t), 3)
    }

# Recovery
class RecoveryManager:
    def __init__(self, path="recovery_cache.json"):
        self.path = path
        self.cache = {'logs': [], 'harmonics': [], 'shields': []}
        self.load()
    def log_event(self, msg): self.cache['logs'].append(msg)
    def save_harmonics(self, pulse): self.cache['harmonics'].append(pulse)
    def shield_event(self, status): self.cache['shields'].append(status)
    def commit(self): open(self.path, 'w').write(json.dumps(self.cache))
    def load(self): 
        if os.path.exists(self.path): 
            self.cache = json.load(open(self.path))

# Obfuscation & Encryption
def obfuscate_pulse(real_pulse):
    noise = {k: round(random.uniform(-1, 1), 3) for k in real_pulse}
    mixed = {k: round((real_pulse[k] + noise[k]) / 2, 3) for k in real_pulse}
    return mixed, noise

def encrypt_glyph(data, salt="glyph_salt"):
    payload = json.dumps(data) + salt
    return hashlib.sha256(payload.encode()).hexdigest()[:12]

# Logging Widget
class LogDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.scroll = ScrollView(size_hint=(1, 0.9))
        self.log_label = Label(text='', size_hint_y=None)
        self.log_label.bind(texture_size=self.update_height)
        self.scroll.add_widget(self.log_label)
        self.add_widget(self.scroll)
        self.add_widget(Label(text='🌐 Overmind Console'))

    def update_height(self, _, val): self.log_label.height = val[1]
    def log(self, msg): self.log_label.text += f"[{time.strftime('%H:%M:%S')}] {msg}\n"

class DroneGlyph(InstructionGroup):
    def __init__(self, x, y, radius, label):
        super().__init__()
        self.x, self.y, self.radius = x, y, radius
        self.color = Color(0.3, 1, 0.7, 1)
        self.circle = Ellipse(pos=(x - radius, y - radius), size=(2 * radius, 2 * radius))
        self.add(self.color)
        self.add(self.circle)

class CometTrail(InstructionGroup):
    def __init__(self, x, y, length):
        super().__init__()
        self.color = Color(0.7, 0.3, 1, 0.5)
        self.line = Line(points=[x, y, x - length, y - length], width=2)
        self.add(self.color)
        self.add(self.line)

class PlanetaryGlyph(InstructionGroup):
    def __init__(self, x, y, radius):
        super().__init__()
        self.color = Color(1, 0.6, 0.2, 1)
        self.body = Ellipse(pos=(x - radius, y - radius), size=(2 * radius, 2 * radius))
        self.add(self.color)
        self.add(self.body)

class ShieldPulse(InstructionGroup):
    def __init__(self, x, y, r=50):
        super().__init__()
        self.color = Color(0.5, 0.8, 1, 0.3)
        self.ring = Line(circle=(x, y, r), width=1.5)
        self.add(self.color)
        self.add(self.ring)

# Console App
class OvermindApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        self.root = Widget()
        self.console = LogDisplay(pos=(10, 10), size_hint=(1, 0.3))
        self.recovery = RecoveryManager()
        self.harmonics = HarmonicResonator()
        self.root.add_widget(self.console)
        Clock.schedule_interval(self.evolve, 1/60.)
        return self.root

    def evolve(self, dt):
        t = time.time()
        pulse = self.harmonics.pulse(t)
        mixed, noise = obfuscate_pulse(pulse)
        encrypted = encrypt_glyph(mixed)
        self.console.log(f"⚙️ Pulse: {pulse} → Glyph: {encrypted}")
        self.recovery.save_harmonics(pulse)
        self.recovery.commit()

        self.root.canvas.clear()
        glyph = DroneGlyph(150 + 200 * random.random(), 300, 10, encrypted)
        comet = CometTrail(glyph.x, glyph.y, 25)
        planet = PlanetaryGlyph(400 + 100 * math.sin(t), 400 + 100 * math.cos(t), 16)
        shield = ShieldPulse(600, 340)

        for g in [glyph, comet, planet, shield]: self.root.canvas.add(g)

if __name__ == '__main__':
    OvermindApp().run()

