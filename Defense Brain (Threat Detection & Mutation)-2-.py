import random
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from threading import Thread
import time

# 🌌 Cosmic Ripple + Particle Burst Layer
class CosmicEffectLayer(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.animate_effects, 0.15)

    def animate_effects(self, dt):
        self.canvas.clear()
        with self.canvas:
            # Ripple effects
            Color(0.2, 0.6, 1.0, 0.3)
            for i in range(3):
                radius = 60 + i * 40 + random.randint(-10, 10)
                Ellipse(pos=(self.center_x - radius / 2, self.center_y - radius / 2), size=(radius, radius))
            
            # Particle bursts
            Color(1.0, 0.7, 0.1, 0.8)
            for _ in range(20):
                x = self.center_x + random.randint(-150, 150)
                y = self.center_y + random.randint(-150, 150)
                Ellipse(pos=(x, y), size=(6, 6))

# 🛰️ Orbital Threat Tracker
class OrbitalDefenseMatrix:
    def __init__(self, callback=None, num_satellites=6):
        self.satellites = [{"id": f"SAT-{i}", "orbit": random.uniform(0.1, 1.0)} for i in range(num_satellites)]
        self.callback = callback

    def scan_loop(self):
        while True:
            scan_data = []
            for sat in self.satellites:
                gravity_flux = random.uniform(0.1, 2.5)
                data = f"[{sat['id']}] Flux: {gravity_flux:.2f} | Orbit: {sat['orbit']:.2f}"
                scan_data.append(data)
            if self.callback:
                self.callback(scan_data)
            time.sleep(3)

# 🧠 GUI Overmind Console
class DefenseGUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.orientation = 'vertical'
        self.effect_layer = CosmicEffectLayer()
        self.add_widget(self.effect_layer)

        self.matrix = OrbitalDefenseMatrix(callback=self.report_threats)
        Thread(target=self.matrix.scan_loop, daemon=True).start()

    def report_threats(self, data):
        print("\n🌀 Orbital Scanners Report:")
        for line in data:
            print("  ", line)

# 🚀 App Launcher
class MythicDefenseApp(App):
    def build(self):
        return DefenseGUI()

if __name__ == '__main__':
    MythicDefenseApp().run()

