active_thoughts = []

def update_thoughts(new_thought):
    if new_thought not in active_thoughts:
        active_thoughts.append(new_thought)
    if len(active_thoughts) > 10:
        active_thoughts.pop(0)

def render_thinking_overlay(canvas, scale=1.0, origin_x=0, origin_y=0):
    canvas.delete("thinking")
    positions = []
    for i, thought in enumerate(active_thoughts):
        x = (100 + i * 100 + i * 10) * scale + origin_x
        y = (60 + i * 5) * scale + origin_y
        positions.append((x, y))
        canvas.create_oval(x-6, y-6, x+6, y+6, fill="cyan", outline="", tags="thinking")
        canvas.create_text(x, y+18, text=thought, fill="white", font=("Helvetica", 8), tags="thinking")
    for i in range(len(positions)-1):
        x1, y1 = positions[i]
        x2, y2 = positions[i+1]
        canvas.create_line(x1, y1, x2, y2, fill="cyan", width=1, tags="thinking")

