# 🚀 main.py — ASI Daemon Launcher
import tkinter as tk
from gui.dashboard import MagicBoxDashboard

def launch_daemon():
    root = tk.Tk()
    app = MagicBoxDashboard(root)
    root.mainloop()

if __name__ == "__main__":
    launch_daemon()

