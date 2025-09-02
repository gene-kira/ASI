# gui.py — MagicBox Daemon Interface
import tkinter as tk
from tkinter import ttk

# Codex Vault (shared reference)
codex_vault = []

# GUI elements (exposed globally)
root = tk.Tk()
root.title("MagicBox Daemon")
root.geometry("900x700")
root.configure(bg="#1c1c2e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 12), background="#1c1c2e", foreground="white")

# Codex Vault Viewer
codex_frame = tk.Frame(root, bg="#1c1c2e")
codex_frame.pack(fill="both", expand=True)

codex_list = tk.Listbox(codex_frame, font=("Courier", 10), bg="#2e2e3e", fg="white", selectbackground="#444")
codex_list.pack(fill="both", expand=True, padx=10, pady=10)

def update_codex_display():
    codex_list.delete(0, tk.END)
    for entry in codex_vault[-50:]:
        codex_list.insert(tk.END, f"{entry['timestamp']} | {entry['source']} | {entry['status']}")

# System Log
log_frame = tk.Frame(root, bg="#1c1c2e")
log_frame.pack(fill="x")

log_label = tk.Label(log_frame, text="System Log:", font=("Arial", 12), bg="#1c1c2e", fg="white")
log_label.pack(anchor="w", padx=10)

log_text = tk.Text(log_frame, height=6, bg="#2e2e3e", fg="white", font=("Courier", 10))
log_text.pack(fill="x", padx=10, pady=5)

def log_output(message):
    log_text.insert(tk.END, message + "\n")
    log_text.see(tk.END)

# Launch GUI loop
def launch_gui():
    log_output("🧿 MagicBox Daemon Interface Ready")
    root.mainloop()

