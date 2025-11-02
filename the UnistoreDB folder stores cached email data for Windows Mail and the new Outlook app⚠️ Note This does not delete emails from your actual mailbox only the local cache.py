import tkinter as tk
from tkinter import scrolledtext
import subprocess
import threading
import os
import time
import ctypes
import sys

# 🔐 Auto-elevate on launch
def elevate():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()

elevate()

# 🧠 Paths
log_path = os.path.expandvars(r"%ProgramData%\CodexPurge\mutation_log.txt")
purge_script = os.path.join(os.getcwd(), "purge_unistoredb.py")

# 🔘 Trigger purge script
def run_purge():
    subprocess.run(["python", purge_script])

# 📜 Refresh mutation log
def refresh_log(text_widget):
    try:
        with open(log_path, "r", encoding="utf-8") as f:
            content = f.read()
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, content)
        text_widget.config(state=tk.DISABLED)
    except:
        text_widget.config(state=tk.NORMAL)
        text_widget.delete(1.0, tk.END)
        text_widget.insert(tk.END, "⚠️ Mutation log not found.")
        text_widget.config(state=tk.DISABLED)

# 🔄 Auto-refresh every 5 seconds
def auto_refresh(text_widget):
    def loop():
        while True:
            refresh_log(text_widget)
            time.sleep(5)
    threading.Thread(target=loop, daemon=True).start()

# 🧿 Launch GUI
def launch_gui():
    root = tk.Tk()
    root.title("Codex Shell: UnistoreDB Purge")
    root.geometry("700x500")

    tk.Label(root, text="🧹 UnistoreDB Cache Purge", font=("Segoe UI", 14, "bold")).pack(pady=10)

    purge_btn = tk.Button(root, text="🔘 Purge Now", font=("Segoe UI", 12), command=run_purge)
    purge_btn.pack(pady=5)

    log_view = scrolledtext.ScrolledText(root, wrap=tk.WORD, font=("Consolas", 10), height=20)
    log_view.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
    log_view.config(state=tk.DISABLED)

    auto_refresh(log_view)
    root.mainloop()

launch_gui()

