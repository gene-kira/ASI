import psutil
import random

# 🧠 Store process dots with motion and metadata
process_dots = {}

# ✅ Define this first so it's available when called
def update_process_map():
    for proc in psutil.process_iter(['pid', 'ppid', 'name']):
        pid = proc.info['pid']
        if pid not in process_dots:
            process_dots[pid] = {
                "x": random.randint(100, 1100),
                "y": random.randint(100, 700),
                "vx": random.uniform(-0.8, 0.8),
                "vy": random.uniform(-0.8, 0.8),
                "name": proc.info['name'],
                "ppid": proc.info['ppid']
            }

# 🎨 Animate process dots and lines with zoom and origin offset
def animate_process_overlay(canvas, scale=1.0, origin_x=0, origin_y=0):
    update_process_map()
    canvas.delete("process")

    for pid, dot in process_dots.items():
        dot["x"] += dot["vx"]
        dot["y"] += dot["vy"]

        # Bounce off edges
        if dot["x"] < 50 or dot["x"] > 1150:
            dot["vx"] *= -1
        if dot["y"] < 50 or dot["y"] > 750:
            dot["vy"] *= -1

        x = dot["x"] * scale + origin_x
        y = dot["y"] * scale + origin_y

        canvas.create_oval(x-4, y-4, x+4, y+4, fill="lime", outline="", tags="process")
        canvas.create_text(x, y+10, text=dot["name"], fill="white", font=("Helvetica", 7), tags="process")

        parent = process_dots.get(dot["ppid"])
        if parent and "x" in parent and "y" in parent:
            px = parent["x"] * scale + origin_x
            py = parent["y"] * scale + origin_y
            canvas.create_line(x, y, px, py, fill="gray", width=1, tags="process")

