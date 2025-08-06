# ━━━━━━━━━ VoidFace Defense GUI • Phylon Prototype ━━━━━━━━━
import math, time, random
from kivy.app import App
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Rectangle
from kivy.core.window import Window

Window.clearcolor = (0, 0, 0, 1)

class VoidFacePanel(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=15, spacing=10, **kwargs)
        self.glyph_log = []

        # Tesla Pulse Meter
        self.pulse_label = Label(text="⚡ Tesla Pulse: 0.00", font_size=20, color=(0.8,1,1,1))
        # Orbital Glyph Display
        self.glyph_label = Label(text="🌌 Orbit: 🔸0 🔸1 🔸2", font_size=18, color=(0.9,0.7,1,1))
        # Threat Evolution Log
        self.log_label = Label(text="[🛡️ Log Console]\n", font_size=16, halign='left', valign='top', color=(1,1,1,1))
        self.log_label.bind(size=self.log_label.setter('text_size'))

        self.add_widget(self.pulse_label)
        self.add_widget(self.glyph_label)
        self.add_widget(self.log_label)

        Clock.schedule_interval(self.update, 1)

    def update(self, dt):
        t = time.time()
        pulse = sum(abs(math.sin(f * t)) for f in [3,6,9]) / 3
        orbit_glyphs = [f"🔸{i}↻{round(math.sin(t + i),2)}" for i in range(3)]
        threat = "⚛️ Plasma Eruption" if pulse > 0.7 else "🌐 Stable Stream"
        self.glyph_log.append(f"[{time.strftime('%H:%M:%S')}] {threat}")

        # Visual feedback updates
        self.pulse_label.text = f"⚡ Tesla Pulse: {pulse:.2f}"
        self.glyph_label.text = "🌌 Orbit: " + " ".join(orbit_glyphs)
        self.log_label.text = "[🛡️ Log Console]\n" + "\n".join(self.glyph_log[-8:])

class VoidFaceApp(App):
    def build(self):
        return VoidFacePanel()

if __name__ == '__main__':
    VoidFaceApp().run()

