# gui.py — Codex Viewer + Game Registration + Ingest Panel
from tkinterdnd2 import TkinterDnD, DND_FILES
import tkinter as tk
from tkinter import ttk
import os
from shared import codex_vault, log_output, update_codex_display
from gameassist import save_known_game
from ingest_data import ingest_file

__all__ = ["launch_gui"]

def launch_gui():
    root = TkinterDnD.Tk()
    root.title("MagicBox Daemon")
    root.geometry("900x800")
    root.configure(bg="#1c1c2e")

    style = ttk.Style()
    style.theme_use("clam")
    style.configure("TLabel", font=("Arial", 12), background="#1c1c2e", foreground="white")
    style.configure("TButton", font=("Arial", 12), padding=6)

    # 📜 Codex Vault Viewer
    codex_list = tk.Listbox(root, font=("Courier", 10), bg="#2e2e3e", fg="white", selectbackground="#444")
    codex_list.pack(fill="both", expand=True, padx=10, pady=10)

    # 🧾 System Log
    log_text = tk.Text(root, height=6, bg="#2e2e3e", fg="white", font=("Courier", 10))
    log_text.pack(fill="x", padx=10, pady=5)

    # 🎮 Game Registration Panel
    def build_game_registration():
        frame = tk.Frame(root, bg="#1c1c2e")
        frame.pack(pady=10)

        tk.Label(frame, text="Register New Game Executable:", bg="#1c1c2e", fg="white").pack(anchor="w", padx=10)
        exe_entry = tk.Entry(frame, font=("Courier", 12), width=40)
        exe_entry.pack(padx=10)

        exe_entry.drop_target_register(DND_FILES)
        exe_entry.dnd_bind('<<Drop>>', lambda e: exe_entry.delete(0, tk.END) or exe_entry.insert(0, os.path.basename(e.data.strip()).lower()))

        tk.Label(frame, text="Game Genre:", bg="#1c1c2e", fg="white").pack(anchor="w", padx=10)
        genre_entry = tk.Entry(frame, font=("Courier", 12), width=40)
        genre_entry.pack(padx=10, pady=5)

        def register_game():
            exe = exe_entry.get().strip().lower()
            genre = genre_entry.get().strip()
            if exe and genre:
                save_known_game(exe, genre)
                log_output(f"[🎮] Registered new game: {exe} ({genre})", log_text)
                exe_entry.delete(0, tk.END)
                genre_entry.delete(0, tk.END)

        ttk.Button(frame, text="Register Game", command=register_game).pack(pady=5)

    # 📂 Ingest Learning Panel
    def build_ingest_panel():
        frame = tk.Frame(root, bg="#1c1c2e")
        frame.pack(pady=10)

        tk.Label(frame, text="Drop Ingest File for Learning:", bg="#1c1c2e", fg="white").pack(anchor="w", padx=10)
        drop_zone = tk.Entry(frame, font=("Courier", 12), width=60)
        drop_zone.pack(padx=10, pady=5)

        drop_zone.drop_target_register(DND_FILES)
        drop_zone.dnd_bind('<<Drop>>', lambda e: ingest_file(e.data.strip(), codex_list, log_text))

    log_output("🧿 MagicBox Daemon Interface Ready", log_text)
    build_game_registration()
    build_ingest_panel()
    update_codex_display(codex_list)
    root.mainloop()

