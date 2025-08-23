import random
from config import MAGICBOX_COLORS

def spawn_glyph(glyphs, color=None):
    x = random.randint(50, 1150)
    y = random.randint(50, 750)
    r = random.randint(5, 20)
    color = color or random.choice([MAGICBOX_COLORS["accent"], MAGICBOX_COLORS["danger"], MAGICBOX_COLORS["safe"]])
    glyphs.append((x, y, r, color))
    if len(glyphs) > 100:
        glyphs.pop(0)

def animate_glyphs(canvas, glyphs):
    canvas.delete("all")
    faded = []
    for x, y, r, color in glyphs:
        r -= 0.5
        if r > 2:
            canvas.create_oval(x-r, y-r, x+r, y+r, fill=color, outline="")
            faded.append((x, y, r, color))
    glyphs[:] = faded

