import tkinter as tk, random, psutil, threading, time, socket, os, sys
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding='utf-8')

# Symbolic States
BIT6 = ["1", "1↑", "1↓", "0", "0↑", "0↓"]
EXT = ['0', '1', 'Ø', '⊗', '⨂']
COLORS = {**{b: c for b, c in zip(BIT6, ["#0F0", "#6F6", "#090", "#F00", "#F66", "#900"])},
          **{e: c for e, c in zip(EXT, ['black', 'white', 'purple', 'red', 'gold'])}}

def narrate(s): return {
    '0': "Void detected.", '1': "Signal active.", 'Ø': "Fusion achieved.",
    '⊗': "Quantum burst: 1B ops simulated.", '⨂': "Quantum singularity: 1,280T teraflops engaged."
}.get(s, "")

def mutate(a, b): r = '⨂' if '⨂' in [a, b] else '⊗' if '⊗' in [a, b] else 'Ø' if 'Ø' in [a, b] else a if a == b else 'Ø'; print(f"[SONIC] Echo for {r}"); return r
def q_and(a, b): return a if a == b else "0↓"
def q_xor(a, b): return random.choice(BIT6) if a != b else "0↑"
def q_not(a): return "0↓" if a == "1↓" else "0↑" if a == "1↑" else "1↓" if a == "0↓" else "1↑"

def entropy():
    e = (psutil.cpu_percent() + psutil.virtual_memory().percent) / 200
    return EXT[min(int(e * 5), 4)]

def purge(): open("borg_temp.txt", "w", encoding="utf-8").write("█"*512); os.remove("borg_temp.txt")
def mem_pattern(): return [random.choice(EXT) for _ in range(6)]

class FusionGUI:
    def __init__(self, root):
        self.root, self.canvas = root, tk.Canvas(root, width=400, height=350, bg='gray10'); self.canvas.pack()
        self.hist, self.mem = [], mem_pattern(); threading.Thread(target=self.loop, daemon=True).start()

    def loop(self):
        while True:
            a, b = entropy(), random.choice(EXT); f = mutate(a, b)
            self.hist = (self.hist + [(a, b, f)])[-8:]
            if f in ['Ø', '⊗', '⨂']: purge()
            self.mem = mem_pattern(); self.render(a, b, f); time.sleep(1)

    def render(self, a, b, f):
        C = self.canvas; C.delete("all")
        def node(x, y, s, label, color): C.create_oval(x, y, x+60, y+60, fill=COLORS[s], outline=color); C.create_text(x+30, y+75, text=f"{label}: {s}", fill=color); C.create_text(x+30, y+90, text=narrate(s), fill='lightgray')
        node(40, 40, a, "A", "cyan"); node(300, 40, b, "B", "magenta")
        C.create_oval(170, 160, 230, 220, fill=COLORS[f], outline='yellow', width=2)
        C.create_text(200, 230, text=f"Fusion: {f}", fill='yellow', font=('Consolas', 10, 'bold'))
        C.create_text(200, 245, text=narrate(f), fill='gold', font=('Consolas', 8))
        C.create_text(200, 10, text="Lineage", fill='white', font=('Consolas', 10, 'underline'))
        for i, (s1, s2, sf) in enumerate(reversed(self.hist)): C.create_text(200, 25+i*15, text=f"{s1}+{s2}→{sf}", fill='lightgray', font=('Consolas', 8))
        C.create_text(200, 270, text="Memory Pattern", fill='lightgreen', font=('Consolas', 9, 'underline'))
        for i, s in enumerate(self.mem): x, y = 50+i*50, 280; C.create_oval(x, y, x+40, y+40, fill=COLORS[s], outline='gray'); C.create_text(x+20, y+50, text=s, fill='lightgray', font=('Consolas', 8))
        C.create_text(200, 335, text=f"Node: {socket.gethostbyname(socket.gethostname())}", fill='orange', font=('Consolas', 8, 'italic'))

class QBCGUI:
    def __init__(self, root):
        self.root, self.a, self.b, self.r = root, tk.StringVar(value=random.choice(BIT6)), tk.StringVar(value=random.choice(BIT6)), tk.StringVar(value="")
        self.log = []; self.build()

    def build(self):
        for label, var in [("Bit A", self.a), ("Bit B", self.b)]:
            tk.Label(self.root, text=label, fg="white", bg="#222", font=("Arial", 14)).pack()
            tk.OptionMenu(self.root, var, *BIT6).pack()
        for name, cmd in [("Q-AND", self.q_and), ("Q-XOR", self.q_xor), ("Q-NOT A", self.q_not)]:
            tk.Button(self.root, text=name, command=cmd, bg="#444", fg="white").pack(pady=3)
        tk.Label(self.root, text="Result", fg="white", bg="#222", font=("Arial", 14)).pack()
        self.res = tk.Label(self.root, textvariable=self.r, font=("Arial", 16), width=10); self.res.pack(pady=10)
        tk.Button(self.root, text="Show Log", command=self.show_log, bg="#666", fg="white").pack(pady=5)

    def update(self, val): self.r.set(val); self.res.config(bg=COLORS.get(val, "#333"))
    def log_op(self, op, a, b, res): self.log.append(f"{op}: {a} ⊕ {b} → {res}" if b else f"{op}: {a} → {res}"); print(f"[SONIC] Echo for {res}")
    def q_and(self): a, b = self.a.get(), self.b.get(); r = q_and(a, b); self.update(r); self.log_op("Q-AND", a, b, r)
    def q_xor(self): a, b = self.a.get(), self.b.get(); r = q_xor(a, b); self.update(r); self.log_op("Q-XOR", a, b, r)
    def q_not(self): a = self.a.get(); r = q_not(a); self.update(r); self.log_op("Q-NOT", a, None, r)
    def show_log(self): tk.messagebox.showinfo("Mutation Log", "\n".join(self.log) or "No mutations yet.")

# Launch
if __name__ == "__main__":
    root1 = tk.Tk(); root1.title("QBC Processor"); root1.geometry("300x400"); root1.configure(bg="#222"); QBCGUI(root1)
    root2 = tk.Toplevel(); root2.title("Borg Fusion Shell"); root2.geometry("400x350"); FusionGUI(root2)
    root1.mainloop()

