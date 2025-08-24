import random

def spawn_glyph(glyphs, color=None):
    x = random.randint(50, 1150)
    y = random.randint(50, 750)
    r = random.randint(5, 20)
    color = color or "cyan"
    glyphs.append((x, y, r, color))
    if len(glyphs) > 100:
        glyphs.pop(0)

def animate_glyphs(canvas, glyphs, scale=1.0, origin_x=0, origin_y=0):
    canvas.delete("glyph")
    for x, y, r, color in glyphs:
        sx = x * scale + origin_x
        sy = y * scale + origin_y
        sr = r * scale
        canvas.create_oval(sx-sr, sy-sr, sx+sr, sy+sr, fill=color, outline="", tags="glyph")

def pulse_glyph(canvas, x, y, scale=1.0, origin_x=0, origin_y=0, color="red"):
    sx = x * scale + origin_x
    sy = y * scale + origin_y
    for r in range(10, 30, 5):
        canvas.create_oval(sx-r, sy-r, sx+r, sy+r, outline=color, width=1, tags="glyph")

