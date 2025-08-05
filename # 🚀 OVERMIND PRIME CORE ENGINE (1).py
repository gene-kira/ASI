# 🚀 OVERMIND PRIME CORE ENGINE

# === Auto-import required libraries ===
import sys
import subprocess

def autoload_libs(libs):
    for lib in libs:
        try:
            __import__(lib)
        except ImportError:
            print(f"📦 Installing missing library: {lib}")
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

autoload_libs(["tkinter", "asyncio", "math", "random", "datetime", "threading"])

# === Now safe to import ===
import tkinter as tk
import asyncio
import random
import math
from datetime import datetime, timedelta
import threading

# === CONFIG FLAGS ===
PERSONAL_DATA_TTL = timedelta(days=1)
BACKDOOR_DATA_SELF_DESTRUCT_DELAY = 3
THREAT_LEVEL = 0.0

# === Async Data Packets ===
class AsyncDataPacket:
    def __init__(self, content, is_personal=False, is_backdoor=False):
        self.content = content
        self.is_personal = is_personal
        self.is_backdoor = is_backdoor
        self.timestamp = datetime.now()

    async def self_destruct(self):
        delay = BACKDOOR_DATA_SELF_DESTRUCT_DELAY if self.is_backdoor else PERSONAL_DATA_TTL.total_seconds()
        await asyncio.sleep(delay)
        print(f"💥 DATA PURGED: {self.content}")
        self.content = None

# === Threat Monitor ===
class ThreatMonitor:
    async def monitor(self):
        global THREAT_LEVEL
        while True:
            THREAT_LEVEL = round(random.uniform(0, 1), 2)
            if THREAT_LEVEL > 0.8:
                print("🛡️ ASI Defense Triggered at", THREAT_LEVEL)
            await asyncio.sleep(5)

# === Persona Pulse Engine ===
class HoloPersona:
    def __init__(self, name, emotion="Calm", intensity=0.5):
        self.name = name
        self.emotion = emotion
        self.intensity = intensity

    async def pulse(self):
        while True:
            print(f"🔮 {self.name} → [{self.emotion}] Pulse Intensity: {self.intensity}")
            await asyncio.sleep(self.intensity)

# === GUI Neural Web Node ===
class Node:
    def __init__(self, canvas, width, height):
        self.canvas = canvas
        self.x = random.randint(50, width - 50)
        self.y = random.randint(50, height - 50)
        self.dx = random.uniform(-1, 1)
        self.dy = random.uniform(-1, 1)
        self.radius = 3

    def move(self, width, height):
        self.x += self.dx
        self.y += self.dy
        if self.x <= 0 or self.x >= width:
            self.dx *= -1
        if self.y <= 0 or self.y >= height:
            self.dy *= -1

    def draw(self, threat):
        flare = "#FF0000" if threat > 0.8 else "#00F7FF"
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill=flare, outline=""
        )

# === Tkinter GUI Engine ===
def launch_gui(async_loop):
    root = tk.Tk()
    root.title("🧠 Overmind Neural Interface")
    root.geometry("720x520")
    root.configure(bg="#0B0E1A")

    canvas_width, canvas_height = 700, 460
    canvas = tk.Canvas(root, width=canvas_width, height=canvas_height,
                       bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    node_count = 40
    nodes = [Node(canvas, canvas_width, canvas_height) for _ in range(node_count)]

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(canvas_width, canvas_height)
            node.draw(THREAT_LEVEL)
        for i in range(node_count):
            for j in range(i + 1, node_count):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    pulse_color = "#FF0000" if THREAT_LEVEL > 0.8 else "#00F7FF"
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill=pulse_color, width=1)
        root.after(30, animate)

    animate()
    root.mainloop()

# === Async Loop Launch Thread ===
def run_async_loop(loop):
    asyncio.set_event_loop(loop)
    loop.run_forever()

# === Overmind System Boot Sequence ===
def overmind_boot():
    loop = asyncio.new_event_loop()
    threading.Thread(target=run_async_loop, args=(loop,), daemon=True).start()

    # Instantiate all modules
    persona = HoloPersona("Echo", emotion="Steady", intensity=0.7)
    monitor = ThreatMonitor()

    # Launch core coroutines
    asyncio.run_coroutine_threadsafe(persona.pulse(), loop)
    asyncio.run_coroutine_threadsafe(monitor.monitor(), loop)
    asyncio.run_coroutine_threadsafe(AsyncDataPacket("Encrypted Log", is_personal=True).self_destruct(), loop)
    asyncio.run_coroutine_threadsafe(AsyncDataPacket("Backdoor Trace", is_backdoor=True).self_destruct(), loop)

    # Launch GUI shell
    launch_gui(loop)

# === EXECUTE OVERMIND PRIME ===
if __name__ == "__main__":
    print("🔥 Overmind Prime Ignition")
    overmind_boot()

