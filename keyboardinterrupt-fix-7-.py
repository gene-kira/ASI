import os
import sys
import ctypes
import subprocess
import signal
import json
import time
import threading
import tkinter as tk
from tkinter import ttk

SESSION_FILE = "active_services.json"
SERVICE_DIR = "services"
os.makedirs(SERVICE_DIR, exist_ok=True)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def elevate():
    script = os.path.abspath(sys.argv[0])
    params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
    ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
    sys.exit()

class DominionDeck(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🧠 DominionDeck v3.6")
        self.geometry("1000x550")
        self.services = {}
        self.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.build_gui()
        self.load_session()
        self.auto_scan()
        self.keep_alive()

    def build_gui(self):
        ttk.Label(self, text="DominionDeck v3.6", font=("Consolas", 20)).pack(pady=10)
        self.tree = ttk.Treeview(self, columns=("Agent", "Status", "Role"), show="headings")
        self.tree.heading("Agent", text="Agent")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Role", text="Persona")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<Double-Button-1>", self.safe(self.clear_tree))

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="🔁 Toggle Service", command=self.safe(self.toggle_service)).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="🛑 Kill All", command=self.safe(self.kill_all)).grid(row=0, column=1, padx=10)

    def launch_script(self, name, path):
        if name in self.services:
            return
        CREATE_NEW_PROCESS_GROUP = 0x00000200
        try:
            proc = subprocess.Popen(
                [sys.executable, path],
                creationflags=CREATE_NEW_PROCESS_GROUP
            )
            self.services[name] = proc
            self.tree.item(name, values=(name, "Running", "Sentinel"))
        except Exception:
            self.tree.item(name, values=(name, "Error", "Rogue"))

    def toggle_service(self):
        selected = self.tree.selection()
        for name in selected:
            path = self.resolve_path(name)
            status = self.tree.set(name, "Status")

            if status == "Running":
                proc = self.services.get(name)
                if proc and proc.poll() is None:
                    try:
                        proc.terminate()
                        proc.wait(timeout=5)
                    except Exception:
                        pass
                self.tree.item(name, values=(name, "Inactive", "Watcher"))
                self.services.pop(name, None)

            elif status == "Inactive" and path:
                self.launch_script(name, path)

    def kill_all(self):
        for name, proc in self.services.items():
            try:
                if proc and proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)
                if self.tree.exists(name):
                    self.tree.item(name, values=(name, "Inactive", "Watcher"))
            except Exception:
                pass
        self.services.clear()

    def clear_tree(self, event=None):
        self.tree.delete(*self.tree.get_children())
        self.scan_scripts()

    def scan_scripts(self):
        for entry in os.listdir(SERVICE_DIR):
            full_path = os.path.join(SERVICE_DIR, entry)
            if os.path.isfile(full_path) and entry.endswith(".py"):
                name = entry
                launch_path = full_path
            elif os.path.isdir(full_path) and os.path.isfile(os.path.join(full_path, "main.py")):
                name = entry
                launch_path = os.path.join(full_path, "main.py")
            else:
                continue

            if not self.tree.exists(name):
                status = "Running" if self.is_script_running(launch_path) else "Inactive"
                persona = "Sentinel" if status == "Running" else "Watcher"
                self.tree.insert("", "end", iid=name, values=(name, status, persona))

    def resolve_path(self, name):
        file_path = os.path.join(SERVICE_DIR, name)
        if os.path.isfile(file_path):
            return file_path
        folder_main = os.path.join(file_path, "main.py")
        if os.path.isfile(folder_main):
            return folder_main
        return None

    def is_script_running(self, path):
        for proc in self.services.values():
            try:
                if proc and proc.poll() is None and os.path.abspath(proc.args[1]) == os.path.abspath(path):
                    return True
            except Exception:
                pass
        return False

    def shutdown(self):
        active = []
        for name, proc in self.services.items():
            try:
                if proc and proc.poll() is None:
                    proc.terminate()
                    proc.wait(timeout=5)
                    path = self.resolve_path(name)
                    if path:
                        active.append(path)
            except Exception:
                pass
        try:
            with open(SESSION_FILE, "w") as f:
                json.dump(active, f)
        except Exception:
            pass
        self.destroy()

    def load_session(self):
        if not os.path.exists(SESSION_FILE):
            return
        try:
            with open(SESSION_FILE, "r") as f:
                paths = json.load(f)
            for path in paths:
                name = os.path.basename(path) if path.endswith(".py") else os.path.basename(os.path.dirname(path))
                if os.path.isfile(path):
                    self.launch_script(name, path)
        except Exception:
            pass

    def auto_scan(self):
        def loop():
            while True:
                self.scan_scripts()
                time.sleep(10)
        threading.Thread(target=loop, daemon=True).start()

    def keep_alive(self):
        self.after(100, self.keep_alive)

    def safe(self, func):
        def wrapper(*args, **kwargs):
            try:
                func(*args, **kwargs)
            except Exception:
                pass
        return wrapper

if __name__ == "__main__":
    if not is_admin():
        elevate()
    app = DominionDeck()
    app.mainloop()

