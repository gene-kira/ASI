# crash_proof_fx.py

import random

def safe_fx(canvas):
    try:
        for _ in range(10):
            x, y = random.randint(50, 650), random.randint(50, 450)
            fx = canvas.create_oval(x, y, x+10, y+10, fill="#ff4444", outline="")
            canvas.after(300, lambda fx=fx: canvas.delete(fx))
        print("🧊 FX rendered safely.")
    except Exception as e:
        print(f"🧊 FX fallback triggered: {e}")
        # Future: Log error, switch to minimal FX mode

