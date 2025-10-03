import tkinter as tk
from tkinter import messagebox
import random

# Define symbolic bit states
BIT_STATES = ["1", "1↑", "1↓", "0", "0↑", "0↓"]
COLOR_MAP = {
    "1": "#00FF00", "1↑": "#66FF66", "1↓": "#009900",
    "0": "#FF0000", "0↑": "#FF6666", "0↓": "#990000"
}

# Mutation logic gates
def q_and(a, b):
    return a if a == b else "0↓"

def q_xor(a, b):
    return random.choice(BIT_STATES) if a != b else "0↑"

def q_not(a):
    if "1" in a:
        return "0↓" if "↓" in a else "0↑"
    elif "0" in a:
        return "1↓" if "↓" in a else "1↑"
    return "0"

# Sonic feedback (simulated)
def emit_sonic_echo(bit):
    print(f"[SONIC] Echo emitted for {bit}")

# Mutation trace log
mutation_log = []

def log_mutation(op, a, b, result):
    entry = f"{op}: {a} ⊕ {b} → {result}" if b else f"{op}: {a} → {result}"
    mutation_log.append(entry)
    emit_sonic_echo(result)

# GUI setup
class QBCGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Quantum Bit Cutting Processor")
        self.root.geometry("500x400")
        self.root.configure(bg="#222")

        self.bit_a = tk.StringVar(value=random.choice(BIT_STATES))
        self.bit_b = tk.StringVar(value=random.choice(BIT_STATES))
        self.result = tk.StringVar(value="")

        self.create_widgets()

    def create_widgets(self):
        tk.Label(self.root, text="Bit A", fg="white", bg="#222", font=("Arial", 14)).pack()
        self.a_menu = tk.OptionMenu(self.root, self.bit_a, *BIT_STATES)
        self.a_menu.pack()

        tk.Label(self.root, text="Bit B", fg="white", bg="#222", font=("Arial", 14)).pack()
        self.b_menu = tk.OptionMenu(self.root, self.bit_b, *BIT_STATES)
        self.b_menu.pack()

        tk.Button(self.root, text="Q-AND", command=self.q_and_op, bg="#444", fg="white").pack(pady=5)
        tk.Button(self.root, text="Q-XOR", command=self.q_xor_op, bg="#444", fg="white").pack(pady=5)
        tk.Button(self.root, text="Q-NOT A", command=self.q_not_op, bg="#444", fg="white").pack(pady=5)

        tk.Label(self.root, text="Result", fg="white", bg="#222", font=("Arial", 14)).pack()
        self.result_label = tk.Label(self.root, textvariable=self.result, font=("Arial", 16), width=10)
        self.result_label.pack(pady=10)

        tk.Button(self.root, text="Show Mutation Log", command=self.show_log, bg="#666", fg="white").pack(pady=10)

    def update_result(self, value):
        self.result.set(value)
        self.result_label.config(bg=COLOR_MAP.get(value, "#333"))

    def q_and_op(self):
        a, b = self.bit_a.get(), self.bit_b.get()
        res = q_and(a, b)
        self.update_result(res)
        log_mutation("Q-AND", a, b, res)

    def q_xor_op(self):
        a, b = self.bit_a.get(), self.bit_b.get()
        res = q_xor(a, b)
        self.update_result(res)
        log_mutation("Q-XOR", a, b, res)

    def q_not_op(self):
        a = self.bit_a.get()
        res = q_not(a)
        self.update_result(res)
        log_mutation("Q-NOT", a, None, res)

    def show_log(self):
        log_text = "\n".join(mutation_log) or "No mutations yet."
        messagebox.showinfo("Mutation Log", log_text)

# Launch GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = QBCGUI(root)
    root.mainloop()

