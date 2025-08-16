import tkinter as tk
from tkinter import Canvas
import uuid

class GUIOverlay:
    def __init__(self, brain):
        self.brain = brain
        self.root = tk.Tk()
        self.root.title("🧠 MagicBox Swarm Sentinel")
        self.root.geometry("900x700")
        self.root.configure(bg="#0f0f1f")

        self.canvas = Canvas(self.root, width=900, height=400, bg="#0f0f1f", highlightthickness=0)
        self.canvas.pack()

        self.status_label = tk.Label(self.root, text="Status: Idle", fg="lime", bg="#0f0f1f", font=("Consolas", 14))
        self.status_label.pack(pady=10)

        self.log_box = tk.Text(self.root, height=10, bg="black", fg="cyan", font=("Consolas", 10))
        self.log_box.pack(fill="x", padx=10)

        self.particles = []
        self.animate_particles()

    def update_status(self, msg):
        self.status_label.config(text=f"Status: {msg}")
        self.log_box.insert(tk.END, msg + "\n")
        self.log_box.see(tk.END)

    def animate_particles(self):
        for _ in range(30):
            x, y = uuid.uuid4().int % 900, uuid.uuid4().int % 400
            dot = self.canvas.create_oval(x, y, x+4, y+4, fill="cyan", outline="")
            self.particles.append(dot)
        self.move_particles()

    def move_particles(self):
        for dot in self.particles:
            dx, dy = uuid.uuid4().int % 3 - 1, uuid.uuid4().int % 3 - 1
            self.canvas.move(dot, dx, dy)
        self.root.after(100, self.move_particles)

    def run(self):
        self.root.mainloop()

