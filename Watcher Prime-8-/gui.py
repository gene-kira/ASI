# gui.py — Mythic Interface with Drag-and-Drop Game Registration
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import ttk
import os

# ✅ Exportable symbols
__all__ = ["codex_vault", "log_output", "update_codex_display", "launch_gui"]

# 📜 Shared symbolic memory stream
codex_vault = []

# 🧱 GUI Root (DnD-enabled)
_root = TkinterDnD.Tk()
_root.title("MagicBox Daemon")
_root.geometry("900x750")
_root.configure(bg="#1c1c2e")

_style = ttk.Style()
_style.theme_use("clam")
_style.configure("TLabel", font=("Arial", 12), background="#1c1c2e", foreground="white")
_style.configure("TButton", font=("Arial", 12), padding=6)

# 📜 Codex Vault Viewer
_codex_list = tk.Listbox(_root, font=("Courier", 10), bg="#2e2e3e", fg="white", selectbackground="#444")
_codex_list.pack(fill="both", expand=True, padx=10, pady=10)

def update_codex_display():
    _codex_list.delete(0, tk.END)
    for entry in codex_vault[-50:]:
        _codex_list.insert(tk.END, f"{entry['timestamp']} | {entry['source']} | {entry['status']}")

# 🧾 System Log
_log_text = tk.Text(_root, height=6, bg="#2e2e3e", fg="white", font=("Courier", 10))
_log_text.pack(fill="x", padx=10, pady=5)

def log_output(message):
    _log_text.insert(tk.END, message + "\n")
    _log_text.see(tk.END)

# 🧠 Shortcut Resolver
def resolve_shortcut(path):
    if path.lower().endswith(".lnk"):
        try:
            import pythoncom
            from win32com.client import Dispatch
            shell = Dispatch("WScript.Shell")
            shortcut = shell.CreateShortcut(path)
            return shortcut.Targetpath
        except:
            return path
    return path

def extract_exe_name(path):
    resolved = resolve_shortcut(path)
    return os.path.basename(resolved).lower()

# 🎮 Game Registration Panel
def _build_game_registration():
    import gameassist  # ✅ Local import avoids circular dependency

    frame = tk.Frame(_root, bg="#1c1c2e")
    frame.pack(pady=10)

    tk.Label(frame, text="Register New Game Executable:", font=("Arial", 12), bg="#1c1c2e", fg="white").pack(anchor="w", padx=10)
    exe_entry = tk.Entry(frame, font=("Courier", 12), width=40)
    exe_entry.pack(padx=10)

    # ✅ Enable drag-and-drop
    exe_entry.drop_target_register(DND_FILES)
    exe_entry.dnd_bind('<<Drop>>', lambda e: exe_entry.delete(0, tk.END) or exe_entry.insert(0, extract_exe_name(e.data.strip())))

    tk.Label(frame, text="Game Genre:", font=("Arial", 12), bg="#1c1c2e", fg="white").pack(anchor="w", padx=10)
    genre_entry = tk.Entry(frame, font=("Courier", 12), width=40)
    genre_entry.pack(padx=10, pady=5)

    def register_game():
        exe = exe_entry.get().strip().lower()
        genre = genre_entry.get().strip()
        if exe and genre:
            gameassist.save_known_game(exe, genre)
            log_output(f"[🎮] Registered new game: {exe} ({genre})")
            exe_entry.delete(0, tk.END)
            genre_entry.delete(0, tk.END)

    ttk.Button(frame, text="Register Game", command=register_game).pack(pady=5)

# 🚀 Launch GUI
def launch_gui():
    log_output("🧿 MagicBox Daemon Interface Ready")
    _build_game_registration()
    _root.mainloop()

