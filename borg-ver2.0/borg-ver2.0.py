# 🧩 AutoLoader: ensures all dependencies are installed
import subprocess, sys
def ensure_package(pkg_name, alias=None):
    try: __import__(alias or pkg_name)
    except ImportError:
        print(f"📦 Installing: {pkg_name}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", pkg_name])
        __import__(alias or pkg_name)
for pkg, alias in [("kivy", "kivy"), ("numpy", "numpy")]: ensure_package(pkg, alias)

# 🌐 Imports
import math, time, hashlib, random
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.clock import Clock
from kivy.uix.label import Label
from kivy.uix.scrollview import ScrollView
from kivy.uix.widget import Widget
from kivy.graphics import Color, Ellipse

# ⚛️ Tesla Harmonics Core
class HarmonicResonator:
    def __init__(self): self.base_freq = 3; self.flow_freq = 6; self.unity_freq = 9
    def tesla_pulse(self, t): return {
        'creation': math.sin(self.base_freq * t),
        'motion': math.sin(self.flow_freq * t),
        'completion': math.sin(self.unity_freq * t)
    }

# 🌌 Plasma Lattice
class PlasmaChannel:
    def __init__(self): self.energy = 0; self.magnetic_field_strength = 0
    def laser_arc_injection(self, laser_intensity, arc_discharge):
        self.energy += laser_intensity + arc_discharge
        self.magnetic_field_strength += laser_intensity * 0.1
    def generate_vortex(self):
        twist = self.magnetic_field_strength * 0.8
        return "🌪️ Vortex Initiated" if twist > 100 else "🔁 Channel Stable"

# 🕳️ Black Hole Time Warp
class EventHorizonNode:
    def __init__(self, mass, proximity): self.mass = mass; self.proximity = proximity
    def time_dilation(self): return 1 / (1 + self.mass * self.proximity**2)
class TemporalGlyph:
    def __init__(self, glyph_id, phase): self.id = glyph_id; self.phase = phase; self.age = 0; self.locked = False
    def evolve(self, time_factor):
        if not self.locked: self.age += time_factor
        if time_factor < 0.1: self.locked = True

# 🧠 Borg Agents
class SwarmAgent:
    def __init__(self, name, glyph): self.name = name; self.glyph = glyph; self.assimilated = False
    def scan_and_assimilate(self, packet):
        if 'pattern' in packet:
            self.glyph += f"::{packet['pattern']}"
            self.assimilated = True
            return f"[Borg:{self.name}] Assimilated → {packet['pattern']}"
        return f"[Borg:{self.name}] Pattern not found"

# 🔐 Collective Defense
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

# ⏳ Temporal Grid
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

# 🎇 Particle Burst FX
class ParticleBurst(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        with self.canvas:
            for _ in range(24):
                Color(random.random(), random.random(), random.random())
                Ellipse(pos=(random.randint(0, 300), random.randint(0, 300)), size=(8, 8))

# 📺 Log UI
class LogDisplay(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.scroll = ScrollView(size_hint=(1, 0.9))
        self.log_label = Label(size_hint_y=None, text='', markup=True)
        self.log_label.bind(texture_size=self.update_height)
        self.scroll.add_widget(self.log_label)
        self.add_widget(self.scroll)
        self.add_widget(Label(text='🌐 Overmind Console', size_hint=(1, 0.1)))
    def update_height(self, _, val): self.log_label.height = val[1]
    def log(self, msg): self.log_label.text += f"[{time.strftime('%H:%M:%S')}] {msg}\n"

# 🧬 Tesla-Dream Update
def fusion_lattice_update(resonator, agents, time_step):
    pulse = resonator.tesla_pulse(time_step)
    for agent in agents:
        if pulse['motion'] > 0.7: agent.glyph += "::⚛️"
    return pulse

# 🧠 Mythic Console UI
class OvermindUI(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', **kwargs)
        self.display = LogDisplay()
        self.add_widget(self.display)
        self.resonator = HarmonicResonator()
        self.channel = PlasmaChannel()
        self.grid = TemporalGrid()
        self.agents = [SwarmAgent(f"𝕭{i}", "🔹") for i in range(3)]
        self.defenders = [BorgNode(f"𝕭{i}", hashlib.sha256(str(i).encode()).hexdigest()[:16]) for i in range(3)]
        Clock.schedule_interval(self.system_pulse, 2)

    def system_pulse(self, dt):
        glyph_id = random.randint(1000, 9999)
        burst = ParticleBurst()
        self.add_widget(burst)
        self.channel.laser_arc_injection(420, 180)
        vortex_status = self.channel.generate_vortex()
        self.display.log(f"⚛️ Pulse → Glyph #{glyph_id} evolving | {vortex_status}")
        if random.random() > 0.6: self.display.log("🛡️ Threat absorbed — Particle burst triggered")
        Clock.schedule_once(lambda _: self.remove_widget(burst), 2)
        for agent in self.agents: self.display.log(agent.scan_and_assimilate({'pattern': 'flow_6'}))
        fusion_lattice_update(self.resonator, self.agents, time_step=33)
        self.grid.update_node("𝕭1", time.time() + random.uniform(0.1, 2.9), "pulse")
        if self.grid.detect_anomaly("𝕭1"): self.display.log("⏳ Time Drift Anomaly Detected")
        for defender in self.defenders:
            threat = f"threat_{random.randint(1000,9999)}"
            self.display.log(defender.scan_threat(threat))
            self.display.log(defender.assimilate())

# 🚀 Launcher
class OvermindApp(App):
    def build(self): return OvermindUI()
if __name__ == "__main__": OvermindApp().run()

