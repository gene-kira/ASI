import tkinter as tk
import random, math, time

# 🧠 SelfMutatingShield – Evolves defense logic in real-time
class SelfMutatingShield:
    def __init__(self):
        self.code_dna = "root_defense_sequence"
        self.mutations = []
        self.threat_log = []
        self.auto_scan_active = False

    def scan_threat(self, vector):
        threat_level = hash(vector) % 10
        self.threat_log.append(vector)
        if threat_level > 6:
            self.mutate(vector)

    def mutate(self, vector):
        patch = f"#patch_{hash(vector)}"
        self.code_dna += f"\n{patch}"
        self.mutations.append(patch)

    def status(self):
        return f"[🧠] Mutations: {len(self.mutations)} | Threats: {len(self.threat_log)}"

# 🕸️ Neural Node Class
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

    def draw(self):
        self.canvas.create_oval(
            self.x - self.radius, self.y - self.radius,
            self.x + self.radius, self.y + self.radius,
            fill="#00F7FF", outline=""
        )

# 🚀 GUI Class with Pulse Face + Neural Web
class MagicBoxGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("DREADNΩVA MagicBox Interface")
        self.root.geometry("1000x600")
        self.root.configure(bg="#0C0F1A")

        self.canvas = tk.Canvas(self.root, width=980, height=500, bg="#0A0C1B", highlightthickness=0)
        self.canvas.pack(pady=20)

        self.shield = SelfMutatingShield()
        self.nodes = [Node(self.canvas, 980, 500) for _ in range(40)]

        # ⚙️ Control Buttons
        button_frame = tk.Frame(self.root, bg="#0C0F1A")
        button_frame.pack()

        tk.Button(button_frame, text="Manual Scan", font=("Consolas", 12), bg="#00F7FF",
                  command=self.manual_scan).pack(side=tk.LEFT, padx=10)

        tk.Button(button_frame, text="Toggle Auto Scan", font=("Consolas", 12), bg="#FFDD00",
                  command=self.toggle_auto_scan).pack(side=tk.LEFT, padx=10)

        self.animate()

    def manual_scan(self):
        vector = f"MANUAL_SCAN_{random.randint(1000, 9999)}"
        self.shield.scan_threat(vector)

    def toggle_auto_scan(self):
        self.shield.auto_scan_active = not self.shield.auto_scan_active

    def animate(self):
        self.canvas.delete("all")

        # 🕸️ Neural Node Drawing
        for node in self.nodes:
            node.move(980, 500)
            node.draw()

        for i in range(len(self.nodes)):
            for j in range(i + 1, len(self.nodes)):
                n1, n2 = self.nodes[i], self.nodes[j]
                dist = math.hypot(n1.x - n2.x, n1.y - n2.y)
                if dist < 150:
                    color = "#00F7FF"
                    self.canvas.create_line(n1.x, n1.y, n2.x, n2.y, fill=color, width=1)

        # 👁️ Holographic Pulse Face
        x, y = 880, 100
        pulse = 16 + math.sin(time.time() * 5) * 6
        face_color = "#FF0033" if len(self.shield.threat_log) > 0 else "#00FFAA"
        self.canvas.create_oval(x - pulse, y - pulse, x + pulse, y + pulse, fill=face_color, outline="")
        self.canvas.create_text(x, y, text="👁️", font=("Consolas", 42), fill="#FFFFFF")
        self.canvas.create_text(x, y + 60, text=self.shield.status(), font=("Consolas", 12), fill="#39FF14")

        # 🕷️ Threat Log Display
        self.canvas.create_text(120, 30, text="Latest Threats:", font=("Consolas", 12), fill="#FFDD00", anchor="w")
        for i, threat in enumerate(self.shield.threat_log[-5:]):
            self.canvas.create_text(120, 50 + i*20, text=f"⚠ {threat}", font=("Consolas", 10), fill="#FF3939", anchor="w")

        # 🔁 Auto Scan Trigger
        if self.shield.auto_scan_active and int(time.time()) % 10 == 0:
            vector = f"AUTO_SCAN_{random.randint(1000,9999)}"
            self.shield.scan_threat(vector)

        self.root.after(80, self.animate)

    def launch(self):
        self.root.mainloop()

# 🔥 Start the System
if __name__ == "__main__":
    print("[🧪] Launching DREADNΩVA MagicBox...")
    gui = MagicBoxGUI()
    gui.launch()

