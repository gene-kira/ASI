import psutil
import random

process_dots = {}
hover_tooltip = None

def update_process_map():
    for proc in psutil.process_iter(['pid', 'ppid', 'name']):
        try:
            pid = proc.info['pid']
            if pid not in process_dots:
                process_dots[pid] = {
                    "x": random.randint(100, 1100),
                    "y": random.randint(100, 700),
                    "vx": random.uniform(-0.8, 0.8),
                    "vy": random.uniform(-0.8, 0.8),
                    "name": proc.info.get('name', 'Unknown'),
                    "ppid": proc.info.get('ppid', 0),
                    "pid": pid,
                    "ip": None,
                    "score": 5,
                    "threat": False
                }

            # Try to get connections safely
            score = 5
            ip = None
            try:
                conns = proc.connections()
                for conn in conns:
                    if conn.raddr and hasattr(conn.raddr, 'ip'):
                        ip = conn.raddr.ip
                        score -= 2
            except Exception:
                pass

            process_dots[pid]["score"] = max(1, score)
            process_dots[pid]["ip"] = ip
            process_dots[pid]["threat"] = score <= 2
        except Exception:
            continue

def get_color(score):
    if score <= 2:
        return "red"
    elif score <= 4:
        return "yellow"
    else:
        return "lime"

def animate_process_overlay(canvas, scale=1.0, origin_x=0, origin_y=0):
    update_process_map()
    canvas.delete("process")
    global hover_tooltip
    mouse_x = canvas.winfo_pointerx() - canvas.winfo_rootx()
    mouse_y = canvas.winfo_pointery() - canvas.winfo_rooty()
    hover_tooltip = None

    for pid, dot in process_dots.items():
        dot["x"] += dot["vx"]
        dot["y"] += dot["vy"]

        if dot["x"] < 50 or dot["x"] > 1150:
            dot["vx"] *= -1
        if dot["y"] < 50 or dot["y"] > 750:
            dot["vy"] *= -1

        x = dot["x"] * scale + origin_x
        y = dot["y"] * scale + origin_y
        color = get_color(dot["score"])

        canvas.create_oval(x-4, y-4, x+4, y+4, fill=color, outline="", tags="process")

        if abs(mouse_x - x) < 10 and abs(mouse_y - y) < 10:
            hover_tooltip = {
                "x": x,
                "y": y,
                "text": f"{dot['name']} (PID {dot['pid']})\nTrust: {dot['score']}\nIP: {dot['ip'] or 'None'}\nThreat: {'Yes' if dot['threat'] else 'No'}"
            }

        parent = process_dots.get(dot["ppid"])
        if parent and "x" in parent and "y" in parent:
            px = parent["x"] * scale + origin_x
            py = parent["y"] * scale + origin_y
            canvas.create_line(x, y, px, py, fill="gray", width=1, tags="process")

    if hover_tooltip:
        tx, ty = hover_tooltip["x"], hover_tooltip["y"]
        canvas.create_rectangle(tx+10, ty+10, tx+210, ty+70, fill="black", outline="white", tags="process")
        canvas.create_text(tx+15, ty+15, anchor="nw", text=hover_tooltip["text"], fill="white", font=("Helvetica", 8), tags="process")

