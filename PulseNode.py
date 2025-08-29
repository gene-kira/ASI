import subprocess
import sys
import os
import ctypes
import tkinter as tk
from tkinter import messagebox
import importlib.util

# 🔐 Auto-admin elevation
def elevate():
    if ctypes.windll.shell32.IsUserAnAdmin():
        return True
    else:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, __file__, None, 1)
        sys.exit()

# 🔄 Autoloader for required libraries
def autoload_libraries():
    missing = []
    for lib in ["numpy", "requests", "psutil", "colorama"]:
        if importlib.util.find_spec(lib) is None:
            missing.append(lib)
    if missing:
        subprocess.check_call([sys.executable, "-m", "pip", "install"] + missing)

# 🖥️ Old Guy Friendly GUI
def launch_gui():
    root = tk.Tk()
    root.title("MagicBoxUI - Themed Edition")
    root.geometry("500x300")
    root.configure(bg="#1e1e2f")

    title = tk.Label(root, text="🧠 MagicBoxUI Daemon", font=("Arial", 20, "bold"), fg="#00ffcc", bg="#1e1e2f")
    title.pack(pady=20)

    status = tk.Label(root, text="Status: Ready to Pulse", font=("Arial", 14), fg="#ffffff", bg="#1e1e2f")
    status.pack(pady=10)

    def start_pulse():
        messagebox.showinfo("PulseNode", "Symbolic sync initiated.\nSwarm nodes online.")
        status.config(text="Status: Syncing...", fg="#00ffcc")

    start_btn = tk.Button(root, text="Start PulseNode", font=("Arial", 16), bg="#00ffcc", fg="#000000", command=start_pulse)
    start_btn.pack(pady=30)

    root.mainloop()

# 🚀 Main Execution
if __name__ == "__main__":
    elevate()
    autoload_libraries()
    launch_gui()

