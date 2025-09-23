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

SESSION_FILE = "agent_state.json"
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
        self.title("🧠 DominionDeck v3.7")
        self.geometry("1000x600")
        self.services = {}
        self.agent_state = {}
        self.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.build_gui()
        self.load_state()
        self.scan_scripts()
        self.auto_scan()
        self.keep_alive()

    def build_gui(self):
        ttk.Label(self, text="DominionDeck v3.7", font=("Consolas", 20)).pack(pady=10)

        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        self.scrollable_frame = ttk.Frame(canvas)

        self.scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        self.tree = ttk.Treeview(self.scrollable_frame, columns=("Agent", "Status", "Role"), show="headings", height=20)
        self.tree.heading("Agent", text="Agent")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Role", text="Persona")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        self.tree.bind("<Double-Button-1>", self.safe(self.clear_tree))

        button_frame = ttk.Frame(self)
        button_frame.pack(pady=5)
        ttk.Button(button_frame, text="🔁 Toggle Service", command=self.safe(self.toggle_service)).grid(row=0, column=0, padx=10)
        ttk.Button(button_frame, text="🛑 Kill All", command=self.safe(self.kill_all)).grid(row=0, column=1, padx=10)
        ttk.Button(button_frame, text="💾 Save State", command=self.safe(self.save_state)).grid(row=0, column=2, padx=10)

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
            self.agent_state[path] = "Running"
        except Exception:
            self.tree.item(name, values=(name, "Error", "Rogue"))
            self.agent_state[path] = "Error"

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
                self.agent_state[path] = "Inactive"

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
                    path = self.resolve_path(name)
                    if path:
                        self.agent_state[path] = "Inactive"
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
                status = self.agent_state.get(launch_path, "Inactive")
                persona = "Sentinel" if status == "Running" else "Watcher"
                self.tree.insert("", "end", iid=name, values=(name, status, persona))
                if status == "Running":
                    self.launch_script(name, launch_path)

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
        self.save_state()
        self.destroy()

    def save_state(self):
        try:
            with open(SESSION_FILE, "w") as f:
                json.dump(self.agent_state, f)
        except Exception:
            pass

    def load_state(self):
        if not os.path.exists(SESSION_FILE):
            return
        try:
            with open(SESSION_FILE, "r") as f:
                self.agent_state = json.load(f)
        except Exception:
            self.agent_state = {}

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

