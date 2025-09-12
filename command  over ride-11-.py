import subprocess
import sys
import os
import ctypes
import tkinter as tk
from tkinter import ttk, filedialog

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

class DominionDeck(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🛡️ Dominion Service Deck")
        self.geometry("1000x600")
        self.script_dir = None
        self.services = {}
        self.folder_history = []
        self.protocol("WM_DELETE_WINDOW", self.shutdown)
        self.build_interface()
        self.keep_alive()

    def build_interface(self):
        ttk.Label(self, text="Dominion Service Deck", font=("Consolas", 20)).pack(pady=10)

        main_frame = ttk.Frame(self)
        main_frame.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.Frame(main_frame)
        left_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10)

        right_frame = ttk.Frame(main_frame)
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

        # 🧠 Folder History List
        ttk.Label(left_frame, text="🧠 Folder History", font=("Consolas", 12)).pack(pady=5)
        self.history_listbox = tk.Listbox(left_frame, height=20, width=40)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.Y)
        self.history_listbox.bind("<<ListboxSelect>>", self.safe(self.select_from_history))

        scrollbar = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=scrollbar.set)

        # 📂 Controls
        ttk.Button(right_frame, text="📁 Pick Folder", command=self.safe(self.pick_folder)).pack(pady=5)
        ttk.Label(right_frame, text="📂 Paste a .py file or folder path below", font=("Consolas", 12)).pack(pady=5)
        self.path_entry = ttk.Entry(right_frame, width=80)
        self.path_entry.pack(pady=5)
        ttk.Button(right_frame, text="📥 Load from Path", command=self.safe(self.load_from_path)).pack(pady=5)

        # 🧬 Script Tree
        self.tree = ttk.Treeview(right_frame, columns=("Status", "Persona"), show="headings")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Persona", text="Persona Role")
        self.tree.pack(fill=tk.BOTH, expand=True, pady=10)

        # 🔧 Action Buttons
        action_frame = ttk.Frame(right_frame)
        action_frame.pack(pady=5)
        ttk.Button(action_frame, text="🔍 Scan & Load", command=self.safe(self.scan_scripts)).grid(row=0, column=0, padx=5)
        ttk.Button(action_frame, text="🧬 Toggle Service", command=self.safe(self.toggle_service)).grid(row=0, column=1, padx=5)
        ttk.Button(action_frame, text="🛑 Kill All", command=self.safe(self.shutdown)).grid(row=0, column=2, padx=5)

    def pick_folder(self):
        folder = filedialog.askdirectory(title="Select Folder to Scan")
        if folder:
            self.set_script_dir(folder)

    def load_from_path(self):
        path = self.path_entry.get().strip()
        if os.path.isfile(path) and path.endswith(".py"):
            folder = os.path.dirname(path)
            self.set_script_dir(folder)
        elif os.path.isdir(path):
            self.set_script_dir(path)
        else:
            self.path_entry.delete(0, tk.END)
            self.path_entry.insert(0, "⚠️ Invalid path")

    def set_script_dir(self, folder):
        self.script_dir = folder
        self.scan_scripts()
        if folder not in self.folder_history:
            self.folder_history.append(folder)
            self.history_listbox.insert(tk.END, folder)

    def select_from_history(self, event):
        selection = self.history_listbox.curselection()
        if selection:
            folder = self.history_listbox.get(selection[0])
            if os.path.isdir(folder):
                self.set_script_dir(folder)

    def scan_scripts(self):
        if not self.script_dir or not os.path.isdir(self.script_dir):
            return
        self.tree.delete(*self.tree.get_children())
        for filename in os.listdir(self.script_dir):
            if filename.endswith(".py"):
                full_path = os.path.join(self.script_dir, filename)
                status = "Running" if self.is_script_running(full_path) else "Inactive"
                persona = "Sentinel" if status == "Running" else "Watcher"
                self.tree.insert("", "end", iid=filename, values=(status, persona))

    def is_script_running(self, path):
        for proc in self.services.values():
            try:
                if proc and proc.poll() is None and os.path.abspath(proc.args[1]) == os.path.abspath(path):
                    return True
            except Exception:
                pass
        return False

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

