import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.boxlayout import BoxLayout
from kivy.graphics import Color, Ellipse
from kivy.clock import Clock
from kivy.core.window import Window
import threading, time, random, math
from queue import Queue
from datetime import datetime, timedelta

# 🖥️ Window setup
Window.size = (800, 600)
Window.clearcolor = (0.05, 0.05, 0.1, 1)

# 🧬 Shared data structures
threat_queue = Queue()
personal_data_store = []
fake_telemetry_log = []

# 🌀 Logging utility
def log(message):
    print(f"[MythicLog] {message}")

# 🕷️ Swarm Agent Logic
def swarm_agent(name):
    while True:
        threat = threat_queue.get()
        if threat:
            log(f"🕷️ {name} analyzing threat: {threat}")
            time.sleep(random.uniform(0.5, 2))
            log(f"✅ {name} neutralized: {threat}")

for i in range(5):
    threading.Thread(target=swarm_agent, args=(f"Agent-{i}",), daemon=True).start()

# 🌌 Holographic Threat Glyph
class ThreatGlyph(Widget):
    def __init__(self, label, radius=100, speed=0.05, **kwargs):
        super().__init__(**kwargs)
        self.label = label
        self.angle = random.uniform(0, 2 * math.pi)
        self.radius = radius
        self.speed = speed
        Clock.schedule_interval(self.animate, 0.05)

    def animate(self, dt):
        self.angle += self.speed
        x = self.center_x + self.radius * math.cos(self.angle)
        y = self.center_y + self.radius * math.sin(self.angle)
        self.canvas.clear()
        with self.canvas:
            Color(1, 0.2, 0.6, 0.8)
            Ellipse(pos=(x - 10, y - 10), size=(20, 20))

# 🔥 Particle Burst Visualizer
class ParticleBurst(Widget):
    def __init__(self, pos, count=40, radius=80, **kwargs):
        super().__init__(**kwargs)
        self.particles = []
        self.pos = pos
        self.radius = radius
        self.count = count
        self.generate_particles()
        Clock.schedule_interval(self.animate, 1/60)

    def generate_particles(self):
        for _ in range(self.count):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(2, 5)
            dx = speed * math.cos(angle)
            dy = speed * math.sin(angle)
            self.particles.append({
                'x': self.pos[0],
                'y': self.pos[1],
                'dx': dx,
                'dy': dy,
                'alpha': 1.0
            })

    def animate(self, dt):
        try:
            self.canvas.clear()
            with self.canvas:
                for p in self.particles:
                    p['x'] += p['dx']
                    p['y'] += p['dy']
                    p['alpha'] -= 0.05
                    if p['alpha'] > 0:
                        Color(1, 0.6, 0.2, p['alpha'])  # Mythic orange glow
                        Ellipse(pos=(p['x'], p['y']), size=(8, 8))
            self.particles = [p for p in self.particles if p['alpha'] > 0]
            if not self.particles and self.parent:
                self.parent.remove_widget(self)
        except Exception as e:
            log(f"⚠️ ParticleBurst error: {e}")

# 🔐 Zero-Trust Firewall
def zero_trust_check(agent_id):
    trusted = agent_id.startswith("Agent-")
    if not trusted:
        log(f"🛑 Zero-trust firewall blocked: {agent_id}")
    return trusted

# 💣 Backdoor Monitor
def monitor_backdoor(data):
    log(f"🚨 Backdoor data detected: {data}")
    def destroy():
        log(f"💥 Data self-destructed: {data}")
        trigger_particle_burst(App.get_running_app().root, data)
    threading.Timer(3, destroy).start()

# 🧬 Personal Data Vault (1-day expiry)
def store_personal_data(data):
    expiry = datetime.now() + timedelta(days=1)
    personal_data_store.append((data, expiry))
    log(f"🔐 Personal data stored (expires in 1 day): {data}")

def purge_expired_personal_data():
    now = datetime.now()
    expired = [d for d, t in personal_data_store if t <= now]
    personal_data_store[:] = [(d, t) for d, t in personal_data_store if t > now]
    for data in expired:
        log(f"💀 Personal data expired: {data}")
        trigger_particle_burst(App.get_running_app().root, data)

# 🛰️ Fake Telemetry Generator
def send_fake_telemetry():
    data = f"telemetry_{random.randint(1000,9999)}"
    fake_telemetry_log.append((data, datetime.now()))
    log(f"🛰️ Fake telemetry sent: {data}")
    def destroy():
        log(f"💨 Fake telemetry self-destructed: {data}")
        trigger_particle_burst(App.get_running_app().root, data)
    threading.Timer(30, destroy).start()

# ⚡ Trigger burst with delay to avoid canvas errors
def trigger_particle_burst(root, label):
    def add_burst(dt):
        burst = ParticleBurst(pos=(Window.width // 2, Window.height // 2))
        root.add_widget(burst)
        log(f"💥 Visual burst triggered for: {label}")
    Clock.schedule_once(add_burst, 0.1)

# 🌌 Main HUD with GUI
class MythicHUD(Widget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        Clock.schedule_interval(self.spawn_threat, 3)
        Clock.schedule_interval(lambda dt: send_fake_telemetry(), 10)
        Clock.schedule_interval(lambda dt: purge_expired_personal_data(), 60)

        # GUI Elements
        self.gui = BoxLayout(orientation='vertical', size_hint=(1, None), height=150)
        self.label = Label(text="Tap the button to trigger a mythic burst!", font_size=24)
        self.button = Button(text="🔥 Activate Burst", size_hint=(1, 0.4), font_size=20)
        self.button.bind(on_press=self.on_button_press)
        self.gui.add_widget(self.label)
        self.gui.add_widget(self.button)
        self.add_widget(self.gui)

    def on_button_press(self, instance):
        self.label.text = "✨ Burst Activated!"
        trigger_particle_burst(self, self.label.text)

    def spawn_threat(self, dt):
        label = f"Threat-{random.randint(1000, 9999)}"
        if zero_trust_check(label):
            glyph = ThreatGlyph(label=label, radius=random.randint(80, 200), speed=random.uniform(0.01, 0.1))
            glyph.center = self.center
            self.add_widget(glyph)
            threat_queue.put(label)
            log(f"⚠️ Threat detected: {label}")
        else:
            monitor_backdoor(label)

# 🚀 App Core
class MythicDefenseApp(App):
    def build(self):
        root = MythicHUD()
        store_personal_data("User: John Doe, SSN: 123-45-6789")
        log("🚀 Mythic Defense Engine Activated")
        return root

# 🚀 Launch
if __name__ == '__main__':
    MythicDefenseApp().run()

