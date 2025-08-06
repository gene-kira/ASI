# AutoLoader & Imports
import subprocess, sys
def ensure_package(pkg, alias=None):
    try: __import__(alias or pkg)
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
        __import__(alias or pkg)
for pkg, alias in [("kivy", "kivy"), ("numpy", "numpy")]: ensure_package(pkg, alias)

import math, time, random, hashlib
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse, Line
from kivy.clock import Clock
from kivy.core.window import Window

# Harmonic Resonator (Tesla 3-6-9 pulses)
class HarmonicResonator:
    def __init__(self): self.base_freq = 3; self.flow_freq = 6; self.unity_freq = 9
    def tesla_pulse(self, t): return {
        'creation': math.sin(self.base_freq * t),
        'motion': math.sin(self.flow_freq * t),
        'completion': math.sin(self.unity_freq * t)
    }

# Fusion lattice updates
def fusion_lattice_update(resonator, agents, time_step):
    pulse = resonator.tesla_pulse(time_step)
    for agent in agents:
        if pulse['motion'] > 0.7: agent.glyph += "::⚛️"
    return pulse

# Plasma Vortex Generator
class PlasmaChannel:
    def __init__(self): self.energy = 0; self.magnetic_field_strength = 0
    def laser_arc_injection(self, laser_intensity, arc_discharge):
        self.energy += laser_intensity + arc_discharge
        self.magnetic_field_strength += laser_intensity * 0.1
    def generate_vortex(self):
        twist = self.magnetic_field_strength * 0.8
        return "🌪️ Vortex Initiated" if twist > 100 else "🔁 Stable Channel"

# Borg Swarm Agent & Defender Logic
class SwarmAgent:
    def __init__(self, name, glyph): self.name = name; self.glyph = glyph; self.assimilated = False
    def scan_and_assimilate(self, packet):
        if 'pattern' in packet:
            self.glyph += f"::{packet['pattern']}"
            self.assimilated = True
            return f"[Borg:{self.name}] Assimilated → {packet['pattern']}"
        return f"[Borg:{self.name}] Pattern not found"

class BorgNode:
    def __init__(self, id, glyph_sig): self.id = id; self.glyph = glyph_sig; self.threat_level = 0; self.learned = set()
    def scan_threat(self, sig):
        digest = hashlib.sha256(sig.encode()).hexdigest()
        if digest[:3] == self.glyph[:3]:
            self.threat_level += 1
            return f"🛡️ {self.id} absorbed → {digest[:12]}"
        else:
            self.learned.add(digest)
            return f"👁️ {self.id} evolved → {digest[:12]}"
    def assimilate(self):
        if self.threat_level >= 3:
            self.glyph = hashlib.sha256((self.glyph + str(time.time())).encode()).hexdigest()[:16]
            self.threat_level = 0
            return f"🚨 {self.id} evolved glyph → {self.glyph}"
        return "✅ Stable"

# Temporal Drift Detection
class TemporalGrid:
    def __init__(self): self.grid_nodes = {}
    def update_node(self, id, stamp, field):
        if id not in self.grid_nodes:
            self.grid_nodes[id] = {'timestamps': [], 'field': field}
        self.grid_nodes[id]['timestamps'].append(stamp)
    def detect_anomaly(self, id):
        times = self.grid_nodes[id]['timestamps']
        if len(times) < 2: return False
        deltas = [times[i+1]-times[i] for i in range(len(times)-1)]
        return max(deltas) - min(deltas) > 1.7

# Visuals: Particles, Spirals, Borg Glyphs
class ParticleBurst(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            for _ in range(24):
                Color(random.random(), random.random(), random.random())
                Ellipse(pos=(random.randint(0, 300), random.randint(0, 300)), size=(8, 8))

class GlyphSpiralOrbit(Widget):
    def __init__(self, center_x=150, center_y=150, radius=80, glyph_count=9, **kwargs):
        super().__init__(**kwargs)
        self.center = (center_x, center_y); self.radius = radius; self.glyph_count = glyph_count
        self.orbit()
    def orbit(self):
        with self.canvas:
            for i in range(self.glyph_count):
                phase = i * 0.3
                spiral_r = self.radius + i * 8
                theta, points = 0, []
                Color(0.3 + 0.05*i, 0.8 - 0.08*i, 1.0, 0.8)
                while theta < 2 * math.pi:
                    r = spiral_r * math.exp(-0.1 * theta)
                    x = self.center[0] + r * math.cos(theta + phase)
                    y = self.center[1] + r * math.sin(theta + phase)
                    points += [x, y]; theta += 0.1
                Line(points=points, width=1.2)

class BorgCube(Widget):
    def on_touch_move(self, touch): self.center = touch.pos
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.2, 0.9, 0.2)
            for offset in range(0, 60, 20): Line(rectangle=(100 + offset, 100 + offset, 40, 40), width=2)

class BorgSpear(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            Color(0.8, 0.1, 0.8)
            Line(points=[200, 100, 240, 200], width=2)
            Line(points=[240, 200, 260, 160], width=2)
            Ellipse(pos=(250, 150), size=(10, 10))

# ━━━━━━━━━ 👑 Borg Queen Glyph Evolution ━━━━━━━━━
class BorgQueen(Widget):
    def __init__(self, evolve_callback=None, **kwargs):
        super().__init__(**kwargs)
        self.evolve_callback = evolve_callback
        with self.canvas:
            Color(1.0, 0.5, 0.2)
            Ellipse(pos=(150, 250), size=(40, 40))
            Line(circle=(170, 270, 25, 0, 360), width=1.5)
            Line(points=[170, 270, 170, 310], width=1.5)
    def on_touch_down(self, touch):
        if self.collide_point(*touch.pos) and self.evolve_callback:
            self.evolve_callback()

# ━━━━━━━━━ 🌐 Log Display Console ━━━━━━━━━
class LogDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.scroll = ScrollView(size_hint=(1, 0.9))
        self.log_label = Label(size_hint_y=None, text='', markup=True)
        self.log_label.bind(texture_size=self.update_height)
        self.scroll.add_widget(self.log_label)
        self.add_widget(self.scroll)
        self.add_widget(Label(text='🌐 Overmind Console', size_hint=(1, 0.1)))

    def update_height(self, _, val):
        self.log_label.height = val[1]

    def log(self, msg):
        self.log_label.text += f"[{time.strftime('%H:%M:%S')}] {msg}\n"

# ━━━━━━━━━ 🧠 Overmind Main UI ━━━━━━━━━
class OvermindUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.display = LogDisplay()
        self.add_widget(self.display)

        # Mythic subsystems
        self.resonator = HarmonicResonator()
        self.channel = PlasmaChannel()
        self.grid = TemporalGrid()
        self.agents = [SwarmAgent(f"𝕭{i}", "🔹") for i in range(4)]
        self.defenders = [BorgNode(f"𝕭{i}", hashlib.sha256(str(i).encode()).hexdigest()[:16]) for i in range(4)]

        Clock.schedule_interval(self.system_pulse, 2)

    def system_pulse(self, dt):
        glyph_id = random.randint(1000, 9999)

        # Cinematic glyph visuals
        burst = ParticleBurst()
        spiral = GlyphSpiralOrbit()
        cube = BorgCube()
        spear = BorgSpear()
        queen = BorgQueen(evolve_callback=self.trigger_evolution)

        for w in [burst, spiral, cube, spear, queen]:
            self.add_widget(w)

        Clock.schedule_once(lambda _: self.remove_widget(burst), 2.5)
        Clock.schedule_once(lambda _: self.remove_widget(spiral), 3)
        Clock.schedule_once(lambda _: self.remove_widget(cube), 4)
        Clock.schedule_once(lambda _: self.remove_widget(spear), 4)
        Clock.schedule_once(lambda _: self.remove_widget(queen), 4)

        # Subsystem updates
        self.channel.laser_arc_injection(420, 180)
        vortex_status = self.channel.generate_vortex()
        self.display.log(f"⚛️ Pulse → Glyph #{glyph_id} evolving | {vortex_status}")
        self.display.log("🧬 Borg symbols deployed: Cube, Spear, Queen initialized.")

        if random.random() > 0.6:
            self.display.log("🛡️ Threat absorbed — Particle burst triggered")

        for agent in self.agents:
            self.display.log(agent.scan_and_assimilate({'pattern': 'flow_6'}))

        fusion_lattice_update(self.resonator, self.agents, time_step=33)

        self.grid.update_node("𝕭1", time.time() + random.uniform(0.1, 2.9), "pulse")
        if self.grid.detect_anomaly("𝕭1"):
            self.display.log("⏳ Time Drift Anomaly Detected")

        for defender in self.defenders:
            threat = f"threat_{random.randint(1000,9999)}"
            self.display.log(defender.scan_threat(threat))
            self.display.log(defender.assimilate())

    def trigger_evolution(self):
        for agent in self.agents:
            agent.glyph += "::👑"
        self.display.log("👑 Borg Queen triggered glyph evolution across swarm.")

# ━━━━━━━━━ 🚀 Launcher ━━━━━━━━━
class OvermindApp(App):
    def build(self):
        Window.clearcolor = (0, 0, 0, 1)
        return OvermindUI()

if __name__ == '__main__':
    OvermindApp().run()

