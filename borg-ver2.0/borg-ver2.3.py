# AutoLoader for dependencies
import subprocess, sys
for pkg in [("kivy",), ("numpy",), ("simpleaudio",)]:
    try: __import__(pkg[0])
    except: subprocess.check_call([sys.executable, "-m", "pip", "install", pkg[0]])

# Imports
import math, random, time, hashlib
import numpy as np, simpleaudio as sa
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse, Line
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.scrollview import ScrollView
from kivy.core.window import Window

# Tesla Harmonics
class HarmonicResonator:
    def __init__(self): self.f3, self.f6, self.f9 = 3, 6, 9
    def pulse(self, t): return {
        '3': math.sin(self.f3 * t),
        '6': math.sin(self.f6 * t),
        '9': math.sin(self.f9 * t)
    }

# Play harmonic sound
def play_tone(freq=440, dur=0.4, vol=0.3):
    fs = 44100
    t = np.linspace(0, dur, int(fs * dur), False)
    wave = np.sin(freq * t * 2 * np.pi) * vol
    audio = (wave * 32767).astype(np.int16)
    sa.play_buffer(audio, 1, 2, fs)

# Orbital Glyphs
class OrbitalGlyph(Widget):
    def __init__(self, center=(200, 200), radius=80, angle=0, label="🔹", **kwargs):
        super().__init__(**kwargs)
        self.center = center
        self.radius = radius
        self.angle = angle
        self.label = Label(text=label, font_size='20sp')
        self.add_widget(self.label)
        Clock.schedule_interval(self.update_orbit, 1/30)

    def update_orbit(self, dt):
        self.angle += 0.05
        x = self.center[0] + self.radius * math.cos(self.angle)
        y = self.center[1] + self.radius * math.sin(self.angle)
        self.label.pos = (x, y)

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
            self.parent.remove_widget(self)

# Borg Vessel
class BorgVessel(Widget):
    def __init__(self, label="🟥 Cube", path_x=150, **kwargs):
        super().__init__(**kwargs)
        self.y = Window.height
        self.label = Label(text=label, pos=(path_x, self.y), font_size='18sp')
        self.add_widget(self.label)
        Clock.schedule_interval(self.fly, 1/60)

    def fly(self, dt):
        self.y -= 2
        self.label.pos = (self.label.pos[0], self.y)

# Planet Core
class PlanetCore(Widget):
    def __init__(self, x, y, mass=5, color=(0.5, 0.8, 1.0), **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(*color, 0.4)
            Ellipse(pos=(x, y), size=(50, 50))

# Live Log Display
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

# Main Interface
class OvermindUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.display = LogDisplay()
        self.add_widget(self.display)

        self.resonator = HarmonicResonator()
        Clock.schedule_interval(self.pulse_cycle, 2)

    def pulse_cycle(self, dt):
        t = time.time() % 60
        pulse = self.resonator.pulse(t)
        self.display.log(f"⚛️ Harmonic Pulse {pulse}")

        # Orbital glyph
        orbit = OrbitalGlyph(center=(200, 250), radius=80 + pulse['6'] * 20)
        self.add_widget(orbit)
        Clock.schedule_once(lambda _: self.remove_widget(orbit), 3)

        # Comet
        comet = ThreatComet(impact_callback=lambda: self.display.log("☄️ Comet impact detected! Glyphs evolved!"))
        self.add_widget(comet)

        # Borg Vessels
        cube = BorgVessel(label="🟥 Borg Cube", path_x=150)
        spear = BorgVessel(label="🔺 Borg Spear", path_x=250)
        self.add_widget(cube); self.add_widget(spear)
        Clock.schedule_once(lambda _: self.remove_widget(cube), 4)
        Clock.schedule_once(lambda _: self.remove_widget(spear), 4)

        # Planet Core
        planet = PlanetCore(x=300, y=300)
        self.add_widget(planet)
        Clock.schedule_once(lambda _: self.remove_widget(planet), 6)

        # Sound
        play_tone(freq=333 + int(pulse['3'] * 100), dur=0.3)

# Launcher
class OvermindApp(App):
    def build(self): return OvermindUI()

if __name__ == '__main__':
    OvermindApp().run()

