# 🧰 Auto-loader
import subprocess, sys
def ensure_libs():
    try:
        import tkinter, pyttsx3, random, math, threading, time, os
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "pyttsx3"])
ensure_libs()

# 🔊 Voice Engine Setup
import pyttsx3, threading, time, tkinter as tk, random, math

engine = pyttsx3.init()
engine.setProperty('rate', 150)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[0].id)

# 🧠 Node Class
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
        if self.x <= 0 or self.x >= width: self.dx *= -1
        if self.y <= 0 or self.y >= height: self.dy *= -1

    def draw(self):
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#00F7FF", outline=""
        )

# 🧿 Holographic Pulse Simulation
def holographic_pulse(canvas, width, height):
    for _ in range(5):
        x, y = random.randint(0, width), random.randint(0, height)
        r = random.randint(10, 30)
        canvas.create_oval(x-r, y-r, x+r, y+r, outline="#FF00FF", width=2)

# 🧨 Self-Destruct Logic
def auto_destruct(data_type, delay_sec):
    def destroy():
        time.sleep(delay_sec)
        print(f"⚠️] {data_type} auto-destructed after {delay_sec}s")
    threading.Thread(target=destroy).start()

# 🧬 Fake Telemetry Generator
def fake_telemetry():
    data = {
        "cpu": random.randint(1, 100),
        "mem": random.randint(1, 100),
        "ip": f"192.168.{random.randint(0,255)}.{random.randint(0,255)}"
    }
    print("[🌀] Fake telemetry:", data)
    auto_destruct("Telemetry", 30)

# 🧠 GUI Launcher
def launch_guardian_gui():
    root = tk.Tk()
    root.title("🧠 The Guardian — MythicNode Defense")
    root.geometry("800x600")
    root.configure(bg="#0B0E1A")

    canvas = tk.Canvas(root, width=780, height=540, bg="#0A0C1B", highlightthickness=0)
    canvas.pack(pady=30)

    nodes = [Node(canvas, 780, 540) for _ in range(40)]

    def animate():
        canvas.delete("all")
        for node in nodes:
            node.move(780, 540)
            node.draw()
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                n1, n2 = nodes[i], nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill="#00F7FF", width=1)
        holographic_pulse(canvas, 780, 540)
        root.after(30, animate)

    def speak_intro():
        engine.say("Guardian activated. Zero trust defense online.")
        engine.runAndWait()

    threading.Thread(target=speak_intro).start()
    animate()
    root.mainloop()

# 🛡️ System Tray Daemon (Mocked)
def guardian_daemon():
    print("[🛡️] Guardian Daemon running silently in background...")
    auto_destruct("MAC/IP", 30)
    auto_destruct("Backdoor Data", 3)
    auto_destruct("Personal Data", 86400)
    fake_telemetry()

# 🧠 Replicator Logic Stub
def replicator_logic():
    print("[🧬] Replicator logic initialized. Awaiting swarm sync...")
    # Future: sync with MythicNode swarm, persona overlays, encrypted codex

# 🧙 MagicBox Launcher
def magicbox():
    threading.Thread(target=guardian_daemon).start()
    threading.Thread(target=replicator_logic).start()
    launch_guardian_gui()

# 🧓 One-Click Entry Point
if __name__ == "__main__":
    print("[🧙] Launching MagicBox Edition — Old Guy Friendly Mode")
    magicbox()

