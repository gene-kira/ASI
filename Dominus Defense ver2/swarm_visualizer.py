# swarm_visualizer.py

import random

def visualize_swarm(canvas):
    colors = ["#00ffff", "#ff00ff", "#ffff00"]
    for _ in range(20):
        x, y = random.randint(50, 650), random.randint(50, 450)
        aura = canvas.create_oval(x, y, x+15, y+15, fill=random.choice(colors), outline="")
        canvas.after(400, lambda aura=aura: canvas.delete(aura))
    print("🌌 Swarm aura trails rendered.")

