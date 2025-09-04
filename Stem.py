import subprocess
import sys

# 🔧 Autoloader: Ensures all mythic modules are summoned
def autoload_libraries():
    required = {
        'PIL': 'Pillow',
        'numpy': 'numpy',
        'pywin32': 'pywin32',
        'opencv-python': 'opencv-python',
        'pygame': 'pygame',
        'tkinterdnd2': 'tkinterdnd2'
    }

    for lib, pip_name in required.items():
        try:
            __import__(lib)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])

autoload_libraries()

# 🎨 GUI Core
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox

# 🧠 Launch MagicBox GUI
def launch_magicbox_gui():
    root = tk.Tk()
    root.title("🜁 MagicBox Daemon 🜄")
    root.geometry("900x600")
    root.configure(bg="#0b0b0b")
    root.resizable(False, False)

    # 🌀 Header
    header = tk.Label(root, text="🜁 MagicBox Daemon 🜄", font=("Orbitron", 28, "bold"), fg="#00ffe0", bg="#0b0b0b")
    header.pack(pady=20)

    # 🧩 Status Panel
    status_frame = tk.Frame(root, bg="#1a1a1a", bd=2, relief="groove")
    status_frame.pack(pady=10, padx=30, fill="x")

    status_label = tk.Label(status_frame, text="Status: Swarm Sync Active", font=("Consolas", 14), fg="#00ff88", bg="#1a1a1a")
    status_label.pack(pady=10)

    # 🜁 Ingest Button
    def ingest_signal():
        status_label.config(text="🜁 Ingesting Signal...")
        root.after(1500, lambda: status_label.config(text="🜂 Mutation Complete"))

    ingest_btn = ttk.Button(root, text="🜁 Ingest Signal", command=ingest_signal)
    ingest_btn.pack(pady=20)

    # 🧬 Sigil Chain Display
    sigil_frame = tk.Frame(root, bg="#0b0b0b")
    sigil_frame.pack(pady=10)

    sigil_chain = tk.Label(sigil_frame, text="🜁 → 🜂 → 🜄", font=("Consolas", 20), fg="#ff00aa", bg="#0b0b0b")
    sigil_chain.pack()

    # 🧠 Tooltip / Codex Hint
    def show_codex_hint():
        messagebox.showinfo("Codex Vault", "🜁 = Ingest\n🜂 = Mutate\n🜄 = Defend\n🜅 = Overlay")

    codex_btn = ttk.Button(root, text="🧠 View Codex Hint", command=show_codex_hint)
    codex_btn.pack(pady=10)

    # 🌀 Footer
    footer = tk.Label(root, text="Codex Vault Secure • Zero Trust Spine Engaged", font=("Consolas", 10), fg="#888", bg="#0b0b0b")
    footer.pack(side="bottom", pady=10)

    root.mainloop()

# 🚀 Launch the GUI
launch_magicbox_gui()

