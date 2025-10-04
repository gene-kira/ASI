import tkinter as tk, random, psutil, threading, time, socket, os, sys, math
from tkinter import messagebox
if hasattr(sys.stdout, "reconfigure"): sys.stdout.reconfigure(encoding='utf-8')

BIT6 = ["1", "1↑", "1↓", "0", "0↑", "0↓"]
EXT = ['0', '1', 'Ø', '⊗', '⨂']
COLORS = dict(zip(BIT6 + EXT, ["#0F0", "#6F6", "#090", "#F00", "#F66", "#900", 'black', 'white', 'purple', 'red', 'gold']))
NARRATE = {'0': "Void detected.", '1': "Signal active.", 'Ø': "Fusion achieved.",
           '⊗': "Quantum burst: 1B ops simulated.", '⨂': "Quantum singularity: 1,280T teraflops engaged."}

def mutate(a, b): r = next((x for x in ['⨂', '⊗', 'Ø'] if x in [a, b]), a if a == b else 'Ø'); print(f"[SONIC] Echo for {r}"); return r
def q_and(a, b): return a if a == b else "0↓"
def q_xor(a, b): return random.choice(BIT6) if a != b else "0↑"
def q_not(a): return {"1↓": "0↓", "1↑": "0↑", "0↓": "1↓"}.get(a, "1↑")
def entropy(): return EXT[min(int((psutil.cpu_percent() + psutil.virtual_memory().percent) / 40), 4)]
def purge(): open("borg_temp.txt", "w", encoding="utf-8").write("█"*512); os.remove("borg_temp.txt")
def mem_pattern(): return random.choices(EXT, k=6)
def time_dilation(t, v): c = 3e8; return round(t / math.sqrt(1 - v**2 / c**2), 6) if v < c else "Invalid"

class QBCSystemGUI:
    def __init__(self, root):
        self.root, self.canvas = root, tk.Canvas(root, width=500, height=500, bg='gray10'); self.canvas.pack()
        self.bit_a, self.bit_b, self.result = tk.StringVar(value=random.choice(BIT6)), tk.StringVar(value=random.choice(BIT6)), tk.StringVar()
        self.log, self.hist, self.mem = [], [], mem_pattern()
        self.build_gui(); threading.Thread(target=self.entropy_loop, daemon=True).start()

    def build_gui(self):
        for label, var in [("Bit A", self.bit_a), ("Bit B", self.bit_b)]:
            tk.Label(self.root, text=label, fg="white", bg="gray10").pack()
            tk.OptionMenu(self.root, var, *BIT6).pack()
        for name, func in [("Q-AND", self.q_and_op), ("Q-XOR", self.q_xor_op), ("Q-NOT A", self.q_not_op)]:
            tk.Button(self.root, text=name, command=func, bg="#444", fg="white").pack(pady=2)
        tk.Label(self.root, text="Result", fg="white", bg="gray10").pack()
        self.res_label = tk.Label(self.root, textvariable=self.result, font=("Arial", 16), width=10); self.res_label.pack(pady=5)
        tk.Button(self.root, text="Show Log", command=lambda: messagebox.showinfo("Mutation Log", "\n".join(self.log) or "No mutations yet."), bg="#666", fg="white").pack(pady=5)

        # Time Dilation UI
        tk.Label(self.root, text="Time Dilation Calculator", fg="lightblue", bg="gray10").pack(pady=10)
        self.time_entry, self.velocity_entry = tk.Entry(self.root), tk.Entry(self.root)
        self.time_entry.pack(); self.time_entry.insert(0, "1")
        self.velocity_entry.pack(); self.velocity_entry.insert(0, "100000000")
        tk.Button(self.root, text="Calculate Time Dilation", command=self.calc_dilation, bg="#222", fg="white").pack(pady=5)
        self.dilation_result = tk.Label(self.root, text="", fg="yellow", bg="gray10"); self.dilation_result.pack()

    def update_result(self, val): self.result.set(val); self.res_label.config(bg=COLORS.get(val, "#333"))
    def log_op(self, op, a, b, r): self.log.append(f"{op}: {a} ⊕ {b} → {r}" if b else f"{op}: {a} → {r}"); print(f"[SONIC] Echo for {r}")
    def q_and_op(self): self.run_op(q_and, "Q-AND")
    def q_xor_op(self): self.run_op(q_xor, "Q-XOR")
    def q_not_op(self): a = self.bit_a.get(); r = q_not(a); self.update_result(r); self.log_op("Q-NOT", a, None, r)
    def run_op(self, func, label): a, b = self.bit_a.get(), self.bit_b.get(); r = func(a, b); self.update_result(r); self.log_op(label, a, b, r)
    def calc_dilation(self): t, v = float(self.time_entry.get()), float(self.velocity_entry.get()); self.dilation_result.config(text=f"Dilated Time: {time_dilation(t, v)} s")

    def entropy_loop(self):
        while True:
            a, b, f = entropy(), random.choice(EXT), mutate(a := entropy(), b := random.choice(EXT))
            self.hist = (self.hist + [(a, b, f)])[-8:]; self.mem = mem_pattern()
            if f in ['Ø', '⊗', '⨂']: purge()
            self.render_entropy(a, b, f); time.sleep(1)

    def render_entropy(self, a, b, f):
        C = self.canvas; C.delete("all")
        def node(x, y, s, label, color): C.create_oval(x, y, x+60, y+60, fill=COLORS[s], outline=color); C.create_text(x+30, y+75, text=f"{label}: {s}", fill=color); C.create_text(x+30, y+90, text=NARRATE.get(s, ""), fill='lightgray')
        node(40, 40, a, "Entropy A", "cyan"); node(300, 40, b, "Entropy B", "magenta")
        C.create_oval(170, 160, 230, 220, fill=COLORS[f], outline='yellow', width=2)
        C.create_text(200, 230, text=f"Fusion: {f}", fill='yellow'); C.create_text(200, 245, text=NARRATE.get(f, ""), fill='gold')
        C.create_text(200, 10, text="Lineage", fill='white')
        for i, (s1, s2, sf) in enumerate(reversed(self.hist)): C.create_text(200, 25+i*15, text=f"{s1}+{s2}→{sf}", fill='lightgray')
        C.create_text(200, 270, text="Memory Pattern", fill='lightgreen')
        for i, s in enumerate(self.mem): x = 50+i*50; C.create_oval(x, 280, x+40, 320, fill=COLORS[s], outline='gray'); C.create_text(x+20, 330, text=s, fill='lightgray')
        C.create_text(200, 355, text=f"Node: {socket.gethostbyname(socket.gethostname())}", fill='orange')

if __name__ == "__main__":
    root = tk.Tk(); root.title("Quantum Bit Cutting — Infused Shell"); root.geometry("500x500")
    QBCSystemGUI(root); root.mainloop()

