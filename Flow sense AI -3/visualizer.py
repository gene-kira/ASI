# visualizer.py

import time

def animate_node_growth(canvas, root, proc, target_radius, color, x):
    current_radius = 10
    steps = 5
    for i in range(steps):
        r = current_radius + (target_radius - current_radius) * (i + 1) / steps
        canvas.delete(f"node_{proc}")
        canvas.create_oval(x, 50, x + r, 50 + r, fill=color, outline="", tags=f"node_{proc}")
        root.update()
        time.sleep(0.02)

def draw_lineage_trail(canvas, lineage, x_start):
    for i in range(len(lineage) - 1):
        x1 = x_start + i * 60
        x2 = x_start + (i + 1) * 60
        canvas.create_line(x1 + 20, 90, x2 + 20, 90, fill="#8888ff", width=2, dash=(4, 2))
        canvas.create_text(x1 + 20, 100, text=lineage[i], fill="white", font=("Segoe UI", 8))

def draw_mutation_flare(canvas, x, radius):
    canvas.create_oval(x - 5, 45, x + radius + 5, 55 + radius, outline="#ff00ff", width=2)

