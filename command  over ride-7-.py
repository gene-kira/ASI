import ctypes
import sys
import os
import time
import tkinter as tk
from tkinter import ttk
import subprocess

# 🔐 Elevation Check
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

# 🔼 Relaunch with Admin Rights
def elevate():
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit()

# 🎬 Mythic Startup Banner
def show_banner():
    banner = tk.Tk()
    banner.title("Dominion Startup")
    banner.geometry("600x300")
    banner.configure(bg="black")
    banner.resizable(False, False)

    tk.Label(banner, text="🛡️ Initializing DominionDeck", font=("Consolas", 20), fg="lime", bg="black").pack(pady=20)
    tk.Label(banner, text="🔐 Elevation: Granted" if is_admin() else "🔐 Elevation: Pending", font=("Consolas", 14), fg="cyan", bg="black").pack(pady=10)
    tk.Label(banner, text="🧬 Persona: Architect\n🧠 Codex Mutation Tree: Bootstrapping...", font=("Consolas", 12), fg="white", bg="black").pack(pady=10)

    banner.after(3000, banner.destroy)
    banner.mainloop()

# 🖥️ DominionDeck GUI Class
class DominionDeck(tk.Tk):
    def __init__(self, script_dir):
        super().__init__()
        self.title("🛡️ Dominion Service Deck")
        self.geometry("800x600")
        self.script_dir = script_dir
        self.services = {}
        self.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.build_interface()
        self.keep_alive()

    def build_interface(self):
        ttk.Label(self, text="Dominion Service Deck", font=("Consolas", 20)).pack(pady=10)

        self.tree = ttk.Treeview(self, columns=("Status", "Persona"), show="headings")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Persona", text="Persona Role")
        self.tree.pack(fill=tk.BOTH, expand=True)

        ttk.Button(self, text="🔍 Scan & Load Scripts", command=self.safe(self.scan_scripts)).pack(pady=5)
        ttk.Button(self, text="🧬 Toggle Selected Service", command=self.safe(self.toggle_service)).pack(pady=5)
        ttk.Button(self, text="🛑 Kill All Services", command=self.safe(self.shutdown)).pack(pady=5)

    def scan_scripts(self):
        self.tree.delete(*self.tree.get_children())
        for filename in os.listdir(self.script_dir):
            if filename.endswith(".py"):
                self.tree.insert("", "end", iid=filename, values=("Inactive", "Watcher"))

    def toggle_service(self):
        selected = self.tree.selection()
        for script in selected:
            status = self.tree.set(script, "Status")
            path = os.path.join(self.script_dir, script)
            if status == "Inactive":
                proc = subprocess.Popen([sys.executable, path])
                self.services[script] = proc
                self.tree.set(script, "Status", "Running")
                self.tree.set(script, "Persona", "Sentinel")
            else:
                proc = self.services.get(script)
                if proc and proc.poll() is None:
                    proc.terminate()
                    proc.wait()
                self.tree.set(script, "Status", "Inactive")
                self.tree.set(script, "Persona", "Watcher")

    def shutdown(self):
        for proc in self.services.values():
            try:
                if proc and proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)
            except Exception:
                pass
        self.destroy()

    def keep_alive(self):
        self.after(100, self.keep_alive)

    def safe(self, func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception:
                pass
        return wrapper

# 🚀 Launch GUI
def launch_gui():
    script_dir = "C:\\Path\\To\\Your\\Scripts"  # 🔧 Replace with your actual path
    app = DominionDeck(script_dir)
    app.mainloop()

# 🧠 Main Execution
if __name__ == "__main__":
    if not is_admin():
        elevate()
    show_banner()
    launch_gui()
