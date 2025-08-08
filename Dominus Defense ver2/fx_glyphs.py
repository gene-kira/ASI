# fx_glyphs.py

import random

def trigger_glyph_fx(canvas, glyph="⚡", color="#ff00ff"):
    for _ in range(10):
        x, y = random.randint(50, 650), random.randint(50, 450)
        size = random.randint(10, 20)
        fx = canvas.create_text(x, y, text=glyph, font=("Segoe UI", size), fill=color)
        canvas.after(500, lambda fx=fx: canvas.delete(fx))

