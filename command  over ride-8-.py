import ctypes
import sys
import os
import tkinter as tk
from tkinter import ttk, filedialog
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

# 🖥️ DominionDeck GUI
class DominionDeck(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛡️ Dominion Service Deck")
        self.geometry("800x600")
        self.script_dir = None
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

        btn_frame = ttk.Frame(self)
        btn_frame.pack(pady=5)

        ttk.Button(btn_frame, text="📁 Pick Folder", command=self.safe(self.pick_folder)).grid(row=0, column=0, padx=5)
        ttk.Button(btn_frame, text="🔍 Scan & Load", command=self.safe(self.scan_scripts)).grid(row=0, column=1, padx=5)
        ttk.Button(btn_frame, text="🧬 Toggle Service", command=self.safe(self.toggle_service)).grid(row=0, column=2, padx=5)
        ttk.Button(btn_frame, text="🛑 Kill All", command=self.safe(self.shutdown)).grid(row=0, column=3, padx=5)

        # Drag-and-drop fallback: use Entry + manual trigger
        drop_label = ttk.Label(self, text="🖱️ Drag a .py file here or paste path below", font=("Consolas", 12))
        drop_label.pack(pady=10)

        self.drop_entry = ttk.Entry(self, width=80)
        self.drop_entry.pack(pady=5)
        ttk.Button(self, text="📂 Load from Path", command=self.safe(self.load_from_entry)).pack(pady=5)

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if folder:
            self.script_dir = folder
            self.scan_scripts()

    def load_from_entry(self):
        path = self.drop_entry.get().strip()
        if path.endswith(".py") and os.path.exists(path):
            self.script_dir = os.path.dirname(path)
            self.scan_scripts()

    def scan_scripts(self):
        if not self.script_dir:
            return
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

# 🚀 Launch Sequence
if __name__ == "__main__":
    if not is_admin():
        elevate()
    app = DominionDeck()
    app.mainloop()

