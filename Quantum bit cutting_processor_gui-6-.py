import tkinter as tk, random, psutil, threading, time, socket, os, sys, math
from tkinter import messagebox
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding='utf-8')

BIT6, EXT = ["1", "1↑", "1↓", "0", "0↑", "0↓"], ['0', '1', 'Ø', '⊗', '⨂']
COLORS = dict(zip(BIT6 + EXT, ["#0F0", "#6F6", "#090", "#F00", "#F66", "#900", 'black', 'white', 'purple', 'red', 'gold']))
NARRATE = {'0': "Void detected.", '1': "Signal active.", 'Ø': "Fusion achieved.", '⊗': "Quantum burst: 1B ops simulated.", '⨂': "Quantum singularity: 1,280T teraflops engaged."}
mutate = lambda a, b: next((x for x in ['⨂', '⊗', 'Ø'] if x in [a, b]), a if a == b else 'Ø')
q_and = lambda a, b: a if a == b else "0↓"
q_xor = lambda a, b: random.choice(BIT6) if a != b else "0↑"
q_not = lambda a: {"1↓": "0↓", "1↑": "0↑", "0↓": "1↓"}.get(a, "1↑")
entropy = lambda: EXT[min(int((psutil.cpu_percent() + psutil.virtual_memory().percent) / 40), 4)]
purge = lambda: (open("borg_temp.txt", "w", encoding="utf-8").write("█"*512), os.remove("borg_temp.txt"))
mem_pattern = lambda: random.choices(EXT, k=6)
time_dilation = lambda t, v: round(t / math.sqrt(1 - v**2 / 9e16), 6) if v < 3e8 else "Invalid"

class ASITimeCortex:
    def __init__(self): self.log = []
    def shift(self, ref, delta, direction):
        try: ref, delta = float(ref), float(delta); shifted = ref + delta if direction == "forward" else ref - delta; symbol = self.symbolize(delta, direction); self.log.append(f"{direction.title()} {delta}s → {symbol} @ {shifted}s"); return shifted, symbol
        except: return "Invalid", "Error: Temporal breach"
    def symbolize(self, delta, direction):
        return ("Stasis Field" if delta == 0 else "Pulse Drift" if delta < 60 else "Phase Sync" if delta < 3600 else "Epoch Warp" if direction == "forward" else "Chrono Reversal")
    def get_log(self): return "\n".join(self.log[-5:]) or "No temporal mutations yet."

class QBCSystemGUI:
    def __init__(self, root):
        self.root, self.canvas = root, tk.Canvas(root, width=500, height=500, bg='gray10'); self.canvas.pack()
        self.bit_a, self.bit_b, self.result = tk.StringVar(), tk.StringVar(), tk.StringVar()
        self.log, self.hist, self.mem, self.wavefronts = [], [], mem_pattern(), []
        self.asi = ASITimeCortex(); self.build_gui(); threading.Thread(target=self.entropy_loop, daemon=True).start()

    def build_gui(self):
        for label, var in [("Bit A", self.bit_a), ("Bit B", self.bit_b)]: tk.Label(self.root, text=label, fg="white", bg="gray10").pack(); tk.OptionMenu(self.root, var, *BIT6).pack()
        for name, func in [("Q-AND", lambda: self.run_op(q_and, "Q-AND")), ("Q-XOR", lambda: self.run_op(q_xor, "Q-XOR")), ("Q-NOT A", lambda: self.run_op(q_not, "Q-NOT", unary=True))]: tk.Button(self.root, text=name, command=func, bg="#444", fg="white").pack(pady=2)
        self.res_label = tk.Label(self.root, textvariable=self.result, font=("Arial", 16), width=10); self.res_label.pack(pady=5)
        tk.Button(self.root, text="Show Log", command=lambda: messagebox.showinfo("Mutation Log", "\n".join(self.log) or "No mutations yet."), bg="#666", fg="white").pack(pady=5)
        self.time_entry, self.velocity_entry = tk.Entry(self.root), tk.Entry(self.root); self.ref_time_entry, self.shift_amount_entry = tk.Entry(self.root), tk.Entry(self.root)
        for e, v in [(self.time_entry, "1"), (self.velocity_entry, "100000000"), (self.ref_time_entry, "3600"), (self.shift_amount_entry, "600")]: e.pack(); e.insert(0, v)
        self.shift_dir = tk.StringVar(value="forward"); tk.OptionMenu(self.root, self.shift_dir, "forward", "backward").pack()
        for label, cmd in [("Calculate Time Dilation", self.calc_dilation), ("Shift Time", self.shift_time), ("Show ASI Log", lambda: messagebox.showinfo("ASI Time Cortex", self.asi.get_log()))]: tk.Button(self.root, text=label, command=cmd, bg="#333", fg="white").pack(pady=5)
        self.dilation_result = tk.Label(self.root, text="", fg="yellow", bg="gray10"); self.dilation_result.pack(); self.shift_result = tk.Label(self.root, text="", fg="cyan", bg="gray10"); self.shift_result.pack()

    def update_result(self, val): self.result.set(val); self.res_label.config(bg=COLORS.get(val, "#333"))
    def run_op(self, func, label, unary=False): a, b = self.bit_a.get(), self.bit_b.get(); r = func(a) if unary else func(a, b); self.update_result(r); self.log.append(f"{label}: {a} ⊕ {b} → {r}" if not unary else f"{label}: {a} → {r}")
    def calc_dilation(self): t, v = float(self.time_entry.get()), float(self.velocity_entry.get()); self.dilation_result.config(text=f"Dilated Time: {time_dilation(t, v)} s")
    def shift_time(self): ref, delta, direction = self.ref_time_entry.get(), self.shift_amount_entry.get(), self.shift_dir.get(); shifted, symbol = self.asi.shift(ref, delta, direction); self.shift_result.config(text=f"{symbol} → {shifted} s"); self.wavefronts.append((time.time(), symbol)); self.wavefronts = self.wavefronts[-5:]

    def entropy_loop(self):
        while True:
            a, b, f = entropy(), random.choice(EXT), mutate(entropy(), random.choice(EXT))
            self.hist = (self.hist + [(a, b, f)])[-8:]; self.mem = mem_pattern()
            if f in ['Ø', '⊗', '⨂']: purge()
            self.render_entropy(a, b, f); time.sleep(1)

    def render_entropy(self, a, b, f):
        self.canvas.delete("all")
        def node(x, y, s, label, color):
            self.canvas.create_oval(x, y, x+60, y+60, fill=COLORS[s], outline=color)
            self.canvas.create_text(x+30, y+75, text=f"{label}: {s}", fill=color)
            self.canvas.create_text(x+30, y+90, text=NARRATE.get(s, ""), fill='lightgray')

        node(40, 40, a, "Entropy A", "cyan")
        node(300, 40, b, "Entropy B", "magenta")

        self.canvas.create_oval(170, 160, 230, 220, fill=COLORS[f], outline='yellow', width=2)
        self.canvas.create_text(200, 230, text=f"Fusion: {f}", fill='yellow')
        self.canvas.create_text(200, 245, text=NARRATE.get(f, ""), fill='gold')

        self.canvas.create_text(200, 10, text="Lineage", fill='white')
        for i, (s1, s2, sf) in enumerate(reversed(self.hist)):
            self.canvas.create_text(200, 25+i*15, text=f"{s1}+{s2}→{sf}", fill='lightgray')

        self.canvas.create_text(200, 270, text="Memory Pattern", fill='lightgreen')
        for i, s in enumerate(self.mem):
            x = 50 + i * 50
            self.canvas.create_oval(x, 280, x + 40, 320, fill=COLORS[s], outline='gray')
            self.canvas.create_text(x + 20, 330, text=s, fill='lightgray')

        self.canvas.create_text(200, 355, text=f"Node: {socket.gethostbyname(socket.gethostname())}", fill='orange', font=('Consolas', 8, 'italic'))
        self.canvas.create_text(200, 370, text="Temporal Wavefronts", fill='cyan', font=('Consolas', 9, 'underline'))
        for i, (ts, label) in enumerate(reversed(self.wavefronts)):
            age = time.time() - ts
            x = 200 + int(40 * math.sin(age))
            y = 385 + i * 15
            self.canvas.create_text(x, y, text=label, fill='cyan', font=('Consolas', 8))
            self.canvas.create_line(x-20, y, x+20, y, fill='cyan', dash=(2, 2))

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Quantum Bit Cutting — ASI Infused Shell")
    root.geometry("500x500")
    QBCSystemGUI(root)
    root.mainloop()



