import tkinter as tk

def setup_feed_canvas(root):
    canvas = tk.Canvas(root, bg="#1e1e2f", width=640, height=180, highlightthickness=0)
    canvas.pack(pady=10)

    nodes = {
        "System": (100, 75),
        "Web": (300, 30),
        "Swarm": (500, 75),
        "ASI": (300, 140)
    }

    for label, (x, y) in nodes.items():
        canvas.create_oval(x-8, y-8, x+8, y+8, fill="#5cdb95")
        canvas.create_text(x, y+15, text=label, fill="#ffffff", font=("Segoe UI", 10))

    return canvas, nodes

def animate_feeds(canvas, nodes):
    canvas.delete("line")
    for source in ["System", "Web", "Swarm"]:
        x1, y1 = nodes[source]
        x2, y2 = nodes["ASI"]
        canvas.create_line(x1, y1, x2, y2, fill="#00ffcc", width=2, tags="line")
    canvas.create_text(nodes["ASI"][0], nodes["ASI"][1]-20, text="🔮", font=("Segoe UI", 24), fill="#ffcc00")

