# missing_link_daemon.py
# Run with: python missing_link_daemon.py

# === Autoloader ===
import subprocess, sys, os
def autoload(packages):
    for pkg in packages:
        try:
            __import__(pkg)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pkg])
autoload(["sympy", "networkx", "matplotlib"])

# === Auto-Elevation (Windows only) ===
if os.name == "nt":
    import ctypes
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

# === Imports ===
import tkinter as tk
from tkinter import messagebox
from sympy import symbols, Eq, solve, sympify
import json, time
from pathlib import Path
import networkx as nx
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

# === Mutation Tracker ===
class MutationLog:
    def __init__(self):
        self.log = []

    def record(self, action, details):
        self.log.append({
            "timestamp": time.time(),
            "action": action,
            "details": details
        })

    def get_log(self):
        return self.log

# === JSON-Based Memory ===
class MemoryStore:
    def __init__(self, filename="missing_link_memory.json"):
        self.path = Path.home() / filename
        if not self.path.exists():
            with open(self.path, "w") as f:
                json.dump([], f)

    def store_case(self, constraints, target, solution):
        case = {
            "timestamp": time.time(),
            "constraints": [str(c) for c in constraints],
            "target": target,
            "solution": str(solution)
        }
        with open(self.path, "r") as f:
            data = json.load(f)
        data.append(case)
        with open(self.path, "w") as f:
            json.dump(data, f, indent=2)

# === Reasoning Core ===
class Reasoner:
    def __init__(self, memory):
        self.constraints = []
        self.variables = {}
        self.memory = memory
        self.mutations = MutationLog()

    def add_constraint(self, expr: str):
        left, right = expr.split("=")
        syms = {n: self.variables.get(n, symbols(n)) for n in expr if n.isalpha()}
        eq = Eq(sympify(left, syms), sympify(right, syms))
        self.constraints.append(eq)
        self.mutations.record("add_constraint", expr)

    def solve_for(self, target: str):
        target_sym = self.variables.get(target, symbols(target))
        self.variables[target] = target_sym
        try:
            sol = solve(self.constraints, target_sym, dict=True)
            self.mutations.record("solve", {"target": target, "solution": sol})
            self.memory.store_case(self.constraints, target, sol)
            return sol
        except Exception as e:
            self.mutations.record("error", str(e))
            return None

# === GUI Overlay ===
class MissingLinkGUI:
    def __init__(self, root, reasoner):
        self.root = root
        self.reasoner = reasoner
        self.root.title("Missing Link Daemon Shell")

        self.fig, self.ax = plt.subplots(figsize=(6, 6))
        self.canvas = FigureCanvasTkAgg(self.fig, master=root)
        self.canvas.get_tk_widget().pack()

        self.entry = tk.Entry(root, width=50)
        self.entry.pack()

        self.var_entry = tk.Entry(root, width=20)
        self.var_entry.pack()

        self.log = tk.Text(root, height=10)
        self.log.pack()

        tk.Button(root, text="Add Constraint", command=self.add_constraint).pack()
        tk.Button(root, text="Solve", command=self.solve).pack()
        tk.Button(root, text="Show Mutations", command=self.show_mutations).pack()

    def add_constraint(self):
        expr = self.entry.get()
        try:
            self.reasoner.add_constraint(expr)
            self.log.insert(tk.END, f"Added: {expr}\n")
            self.entry.delete(0, tk.END)
            self.refresh_graph()
        except Exception as e:
            messagebox.showerror("Error", f"Failed to add constraint:\n{e}")

    def solve(self):
        var = self.var_entry.get()
        result = self.reasoner.solve_for(var)
        self.log.insert(tk.END, f"Solving for {var} → {result}\n")
        self.refresh_graph()

    def show_mutations(self):
        for m in self.reasoner.mutations.get_log():
            self.log.insert(tk.END, f"[{time.ctime(m['timestamp'])}] {m['action']}: {m['details']}\n")

    def refresh_graph(self):
        self.ax.clear()
        G = nx.Graph()
        for i, eq in enumerate(self.reasoner.constraints):
            cname = f"eq:{i}"
            G.add_node(cname)
            for sym in eq.free_symbols:
                vname = str(sym)
                G.add_node(vname)
                G.add_edge(cname, vname)
        nx.draw(G, with_labels=True, ax=self.ax)
        self.canvas.draw()

# === Launch Daemon ===
def main():
    memory = MemoryStore()
    reasoner = Reasoner(memory)
    root = tk.Tk()
    app = MissingLinkGUI(root, reasoner)
    root.geometry("800x700")
    root.mainloop()

if __name__ == "__main__":
    main()

