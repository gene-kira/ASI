# AutoLoader for dependencies
import subprocess, sys
for pkg in [("kivy",), ("numpy",), ("simpleaudio",)]:
    try: __import__(pkg[0])
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg[0]])

# Imports
import math, random, time, hashlib, json, os, platform
import numpy as np, simpleaudio as sa
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line, InstructionGroup
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Tesla Harmonics
class HarmonicResonator:
    def __init__(self): self.f3, self.f6, self.f9 = 3, 6, 9
    def pulse(self, t): return {
        '3': round(math.sin(self.f3 * t), 3),
        '6': round(math.sin(self.f6 * t), 3),
        '9': round(math.sin(self.f9 * t), 3)
    }

# Recovery & Hybridization
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

def obfuscate_pulse(real_pulse):
    noise = {k: round(random.uniform(-1, 1), 3) for k in real_pulse}
    mixed = {k: round((real_pulse[k] + noise[k]) / 2, 3) for k in real_pulse}
    return mixed, noise

def encrypt_glyph(data, salt="glyph_salt"):
    payload = json.dumps(data) + salt
    return hashlib.sha256(payload.encode()).hexdigest()[:12]

# Sound Engine
def play_tone(freq=440, dur=0.4, vol=0.3):
    try:
        fs = 44100
        t = np.linspace(0, dur, int(fs * dur), False)
        wave = np.sin(freq * t * 2 * np.pi) * vol
        audio = (wave * 32767).astype(np.int16)
        sa.play_buffer(audio, 1, 2, fs)
    except Exception as e:
        print(f"[Sound Error]: {e}")

# Log Display
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
        self.label = label
        self.color = Color(0.2, 1, 0.6, 1)
        self.body = Ellipse(pos=(x - radius, y - radius), size=(2*radius, 2*radius))
        self.text = Label(text=label, pos=(x, y), font_size='12sp')
        self.add(self.color)
        self.add(self.body)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy
        self.body.pos = (self.x - self.radius, self.y - self.radius)

class CometTrail(InstructionGroup):
    def __init__(self, x, y, length):
        super().__init__()
        self.color = Color(0.8, 0.4, 1, 0.6)
        self.trail = Line(points=[x, y, x - length, y - length], width=1.5)
        self.add(self.color)
        self.add(self.trail)

class PlanetaryGlyph(InstructionGroup):
    def __init__(self, x, y, radius):
        super().__init__()
        self.color = Color(1, 0.8, 0.2, 1)
        self.body = Ellipse(pos=(x - radius, y - radius), size=(2 * radius, 2 * radius))
        self.add(self.color)
        self.add(self.body)

class ShieldPulse(InstructionGroup):
    def __init__(self, x, y, max_radius=60):
        super().__init__()
        self.color = Color(0.4, 0.7, 1, 0.5)
        self.ring = Line(circle=(x, y, max_radius), width=1)
        self.add(self.color)
        self.add(self.ring)

# Master Console App
class OvermindApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        self.root = Widget()
        self.console = LogDisplay(pos=(10, 10), size_hint=(1, 0.3))
        self.recovery = RecoveryManager()
        self.harmonics = HarmonicResonator()
        self.glyphs = []

        self.root.add_widget(self.console)
        Clock.schedule_interval(self.evolve, 1/60.)
        return self.root

    def evolve(self, dt):
        t = time.time()
        pulse = self.harmonics.pulse(t)
        mixed, noise = obfuscate_pulse(pulse)
        encrypted = encrypt_glyph(mixed)
        play_tone(220 + int(50 * pulse['3']))

        self.console.log(f"Pulse ϟ {pulse} → Encrypted: {encrypted}")
        self.recovery.save_harmonics(pulse)
        self.recovery.commit()

        # Visual update
        self.root.canvas.clear()
        glyph = DroneGlyph(100 + 200 * random.random(), 300, 12, encrypted)
        comet = CometTrail(glyph.x, glyph.y, 30)
        planet = PlanetaryGlyph(400 + 100 * math.sin(t), 400 + 100 * math.cos(t), 20)
        shield = ShieldPulse(600, 350)

        for g in [glyph, comet, planet, shield]: self.root.canvas.add(g)

if __name__ == '__main__':
    OvermindApp().run()

