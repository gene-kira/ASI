# === AutoLoader ===
import importlib
import subprocess
import sys

def ensure_libs(libs):
    for lib in libs:
        try:
            importlib.import_module(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", lib])

ensure_libs(["sympy", "tkinter"])

# === Imports ===
from sympy import symbols, Eq, solve, latex
from sympy.parsing.sympy_parser import parse_expr
from threading import Lock
import tkinter as tk
from tkinter import ttk

# === Mutation Log ===
class MutationLog:
    def __init__(self):
        self.entries = []

    def record(self, action, detail):
        self.entries.append({"action": action, "detail": detail})

    def get_log(self):
        return self.entries

# === Memory Stub ===
class MemoryDaemon:
    def __init__(self):
        self.cases = []

    def store_case(self, constraints, target, solution):
        self.cases.append({"constraints": constraints, "target": target, "solution": solution})

# === Codex Reasoner ===
class CodexReasoner:
    def __init__(self, memory, mutation_log):
        self.constraints = []
        self.variables = {}
        self.memory = memory
        self.mutations = mutation_log
        self.lock = Lock()

    def _parse_variables(self, expr: str):
        tokens = set(filter(str.isalpha, expr.replace(" ", "").replace("=", "")))
        for token in tokens:
            if token not in self.variables:
                self.variables[token] = symbols(token)
        return self.variables

    def add_constraint(self, expr: str):
        try:
            with self.lock:
                left, right = expr.split("=")
                syms = self._parse_variables(expr)
                eq = Eq(parse_expr(left, local_dict=syms), parse_expr(right, local_dict=syms))
                self.constraints.append(eq)
                self.mutations.record("add_constraint", expr)
        except Exception as e:
            self.mutations.record("error", f"Invalid constraint '{expr}': {str(e)}")

    def solve_for(self, target: str):
        try:
            with self.lock:
                target_sym = self.variables.get(target, symbols(target))
                self.variables[target] = target_sym
                sol = solve(self.constraints, target_sym, dict=True)
                self.mutations.record("solve", {"target": target, "solution": sol})
                self.memory.store_case(self.constraints, target, sol)
                return sol
        except Exception as e:
            self.mutations.record("error", str(e))
            return None

    def visualize_constraints(self):
        return [latex(eq) for eq in self.constraints]

# === GUI Overlay ===
class ConstraintPanel(tk.Frame):
    def __init__(self, master, reasoner):
        super().__init__(master)
        self.reasoner = reasoner
        self.pack()
        self.create_widgets()

    def create_widgets(self):
        self.title = ttk.Label(self, text="🧠 Codex Constraint Ledger", font=("Consolas", 14))
        self.title.pack(pady=10)

        self.text = tk.Text(self, wrap=tk.WORD, width=80, height=20, font=("Consolas", 10))
        self.text.pack()

        self.refresh_btn = ttk.Button(self, text="Refresh Constraints", command=self.refresh)
        self.refresh_btn.pack(pady=5)

    def refresh(self):
        self.text.delete("1.0", tk.END)
        for latex_str in self.reasoner.visualize_constraints():
            self.text.insert(tk.END, f"{latex_str}\n\n")

# === Ritual Launch ===
if __name__ == "__main__":
    memory = MemoryDaemon()
    mutations = MutationLog()
    reasoner = CodexReasoner(memory, mutations)

    # Sample constraints
    reasoner.add_constraint("telemetry_level + user_consent = 0")
    reasoner.add_constraint("diagnostic_level <= 1")

    root = tk.Tk()
    root.title("Codex Reasoner Daemon")
    panel = ConstraintPanel(root, reasoner)
    root.mainloop()

