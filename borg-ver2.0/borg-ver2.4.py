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
    fs = 44100
    t = np.linspace(0, dur, int(fs * dur), False)
    wave = np.sin(freq * t * 2 * np.pi) * vol
    audio = (wave * 32767).astype(np.int16)
    sa.play_buffer(audio, 1, 2, fs)

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

# Reactive Orbital Glyphs
class OrbitalGlyph(Widget):
    def __init__(self, center=(200, 250), radius=80, angle=0, label="🔹", glow=0.5, **kwargs):
        super().__init__(**kwargs)
        self.center = center
        self.radius = radius
        self.angle = angle
        self.label = Label(text=label, font_size=f'{20 + glow * 10}sp', color=(1, 1 - glow, glow, 1))
        self.add_widget(self.label)
        Clock.schedule_interval(self.update_orbit, 1/30)

    def update_orbit(self, dt):
        self.angle += 0.05
        x = self.center[0] + self.radius * math.cos(self.angle)
        y = self.center[1] + self.radius * math.sin(self.angle)
        self.label.pos = (x, y)

# Ambient Particle Burst
class ParticleBurst(InstructionGroup):
    def __init__(self, x, y, count=12):
        super().__init__()
        for _ in range(count):
            dx, dy = random.uniform(-20, 20), random.uniform(-20, 20)
            with self:
                Color(random.random(), 0.5, 1, 1)
                self.add(Ellipse(pos=(x + dx, y + dy), size=(8, 8)))

# Comet Threats
class ThreatComet(Widget):
    def __init__(self, impact_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.x, self.y = random.randint(0, Window.width), Window.height
        self.label = Label(text="☄️", pos=(self.x, self.y), font_size='22sp')
        self.add_widget(self.label)
        self.impact_callback = impact_callback
        Clock.schedule_interval(self.fly, 1/60)

    def fly(self, dt):
        self.y -= 3
        self.label.pos = (self.x, self.y)
        if self.y < 50 and self.impact_callback:
            self.impact_callback()
            self.parent.canvas.add(ParticleBurst(self.x, self.y))
            self.parent.remove_widget(self)

# Borg Vessel + Drone Swarm
class BorgVessel(Widget):
    def __init__(self, label="🟥 Cube", path_x=150, drop_drones=True, **kwargs):
        super().__init__(**kwargs)
        self.y = Window.height
        self.label = Label(text=label, pos=(path_x, self.y), font_size='18sp')
        self.add_widget(self.label)
        Clock.schedule_interval(self.fly, 1/60)
        if drop_drones:
            for _ in range(3): self.spawn_drone(path_x)

    def fly(self, dt):
        self.y -= 2
        self.label.pos = (self.label.pos[0], self.y)

    def spawn_drone(self, target_x):
        drone = Label(text="🔸", font_size='14sp')
        drone.pos = (self.label.pos[0], self.y)
        self.add_widget(drone)
        def swarm(_): drone.pos = (
            drone.pos[0] + (target_x - drone.pos[0]) * 0.05,
            drone.pos[1] - 2
        )
        Clock.schedule_interval(swarm, 1/60)

# Shield Ring
class ShieldRing(Widget):
    def __init__(self, strength=1.0, center=(200, 250), **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.2, 0.9, 1, 0.3)
            Ellipse(pos=(center[0]-60, center[1]-60), size=(120, 120))

# Planet Core
class PlanetCore(Widget):
    def __init__(self, x, y, color=(0.5, 0.8, 1.0), **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color, 0.4)
            Ellipse(pos=(x, y), size=(50, 50))

# Main Interface
class OvermindUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.display = LogDisplay()
        self.add_widget(self.display)
        self.recovery = RecoveryManager()
        self.resonator = HarmonicResonator()
        Clock.schedule_interval(self.pulse_cycle, 2)

    def pulse_cycle(self, dt):
        t = time.time() % 60
        pulse = self.resonator.pulse(t)
        hybrid, noise = obfuscate_pulse(pulse)
        hash = encrypt_glyph(hybrid)

        self.display.log(f"⚛️ Harmonic Pulse → {hash}")
        self.recovery.log_event(f"Pulse: {hybrid}, Noise: {noise}")
        self.recovery.save_harmonics(hybrid)

        # Glyph mutation
        glow = abs(pulse['9'])
        glyph = OrbitalGlyph(center=(200, 250), radius=80 + pulse['6'] * 20, glow=glow)
        self.add_widget(glyph)
        Clock.schedule_once(lambda _: self.remove_widget(glyph), 3)

        # Shield logic
        shields_up = all(v > 0.5 for v in pulse.values())
        if shields_up:
            self.display.log("🛡️ Shields active! Comet deflected.")
            self.recovery.shield_event("active")
            self.add_widget(ShieldRing())
        else:
            comet = ThreatComet(impact_callback=lambda: self.display.log("☄️ Impact! Pulse disrupted."))
            self.add_widget(comet)

        # Borg Vessels + drones
        cube = BorgVessel("🟥 Borg Cube", 150)
        spear = BorgVessel("🔺 Borg Spear", 250)
        self.add_widget(cube); self.add_widget(spear)
        Clock.schedule_once(lambda _: self.remove_widget(cube), 4)
        Clock.schedule_once(lambda _: self.remove_widget(spear), 4)

        # Planet Core
        planet = PlanetCore(300, 300)
        self.add_widget(planet)
        Clock.schedule_once(lambda _: self.remove_widget(planet), 6)

        # Sound
        play_tone(freq=333 + int(pulse['3'] * 100), dur=0.3)

# Launcher
class OvermindApp(App):
    def build(self): return OvermindUI()

if __name__ == '__main__':
    OvermindApp().run()

