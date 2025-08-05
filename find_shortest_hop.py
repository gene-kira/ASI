import sys
import subprocess
import importlib

# 📦 Auto-loader: Installs missing libraries
required_libs = ['networkx', 'matplotlib', 'tkinter']
for lib in required_libs:
    try:
        importlib.import_module(lib)
    except ImportError:
        subprocess.check_call([sys.executable, '-m', 'pip', 'install', lib])

import tkinter as tk
from tkinter import messagebox, filedialog
import networkx as nx
import matplotlib.pyplot as plt

# 🧠 ASI-like tracker placeholder (could be expanded to memory logging + threat eval)
class ASILogger:
    def __init__(self):
        self.logs = []

    def log(self, message):
        self.logs.append(message)
        print(f"[ASI-Log] {message}")

    def get_logs(self):
        return '\n'.join(self.logs)

# 📦 MagicBox Hopper Core
class MagicBoxHopper:
    def __init__(self, asi):
        self.G = nx.Graph()
        self.asi = asi

    def load_graph(self, path):
        try:
            with open(path, 'r') as f:
                for line in f:
                    src, dst, weight = line.strip().split(',')
                    self.G.add_edge(src, dst, weight=int(weight))
            self.asi.log(f"Loaded graph from {path}")
        except Exception as e:
            self.asi.log(f"Failed to load graph: {e}")

    def shortest_hop(self, start, end):
        try:
            path = nx.shortest_path(self.G, source=start, target=end, weight='weight')
            self.asi.log(f"Shortest path from {start} to {end}: {path}")
            return path
        except Exception as e:
            self.asi.log(f"Error finding path: {e}")
            return []

# 🎛 GUI: MagicBox Theme
class MagicBoxGUI:
    def __init__(self, hopper):
        self.hopper = hopper
        self.root = tk.Tk()
        self.root.title("MagicBox Hopper 🌟")
        self.root.geometry("400x300")
        self.root.configure(bg="#1e1e2f")

        tk.Label(self.root, text="Start Node:", bg="#1e1e2f", fg="white").pack()
        self.start_entry = tk.Entry(self.root)
        self.start_entry.pack()

        tk.Label(self.root, text="End Node:", bg="#1e1e2f", fg="white").pack()
        self.end_entry = tk.Entry(self.root)
        self.end_entry.pack()

        tk.Button(self.root, text="Load Graph File", command=self.load_graph).pack(pady=5)
        tk.Button(self.root, text="Find Shortest Hop", command=self.find_shortest_hop).pack(pady=5)
        tk.Button(self.root, text="Show ASI Logs", command=self.show_logs).pack(pady=5)

    def load_graph(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
        if file_path:
            self.hopper.load_graph(file_path)

    def find_shortest_hop(self):
        start = self.start_entry.get()
        end = self.end_entry.get()
        path = self.hopper.shortest_hop(start, end)
        messagebox.showinfo("Shortest Hop", f"Shortest path: {path}")

    def show_logs(self):
        logs = self.hopper.asi.get_logs()
        messagebox.showinfo("ASI Tracker Logs", logs)

    def run(self):
        self.root.mainloop()

# 🚀 Launch the MagicBox
if __name__ == '__main__':
    asi_logger = ASILogger()
    hopper = MagicBoxHopper(asi_logger)
    gui = MagicBoxGUI(hopper)
    gui.run()

