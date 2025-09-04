import tkinter as tk
from tkinter import ttk, messagebox

def launch_magicbox_gui(on_mutation=None, on_defense=None):
    root = tk.Tk()
    root.title("🜁 MagicBox Daemon 🜄")
    root.geometry("900x600")
    root.configure(bg="#0b0b0b")
    root.resizable(False, False)

    # Header
    header = tk.Label(root, text="🜁 MagicBox Daemon 🜄", font=("Helvetica", 28, "bold"), fg="#00ffe0", bg="#0b0b0b")
    header.pack(pady=20)

    # Status Panel
    status_frame = tk.Frame(root, bg="#1a1a1a", bd=2, relief="groove")
    status_frame.pack(pady=10, padx=30, fill="x")

    status_label = tk.Label(status_frame, text="Status: Swarm Sync Active", font=("Consolas", 14), fg="#00ff88", bg="#1a1a1a")
    status_label.pack(pady=10)

    # Ingest Button
    def ingest_signal():
        status_label.config(text="🜁 Ingesting Signal...")
        root.after(1500, lambda: status_label.config(text="🜂 Mutation Complete"))

    ingest_btn = ttk.Button(root, text="🜁 Ingest Signal", command=ingest_signal)
    ingest_btn.pack(pady=20)

    # Sigil Chain Display
    sigil_frame = tk.Frame(root, bg="#0b0b0b")
    sigil_frame.pack(pady=10)

    sigil_chain = tk.Label(sigil_frame, text="🜁 → 🜂 → 🜄", font=("Consolas", 20), fg="#ff00aa", bg="#0b0b0b")
    sigil_chain.pack()

    # Codex Hint
    def show_codex_hint():
        messagebox.showinfo("Codex Vault", "🜁 = Ingest\n🜂 = Mutate\n🜄 = Defend\n🜅 = Overlay\n🛡️ = Autonomous Defense")

    codex_btn = ttk.Button(root, text="🧠 View Codex Hint", command=show_codex_hint)
    codex_btn.pack(pady=10)

    # Footer
    footer = tk.Label(root, text="Codex Vault Secure • Zero Trust Spine Engaged", font=("Consolas", 10), fg="#888", bg="#0b0b0b")
    footer.pack(side="bottom", pady=10)

    # Mutation Feedback
    def mutation_feedback():
        status_label.config(text="🜂 Mutation Triggered")
        sigil_chain.config(text="🜁 → 🜂 → 🜄 → 🜆")

    # Defense Feedback
    def defense_feedback():
        status_label.config(text="🛡️ Defense ASI Activated")
        sigil_chain.config(text="🜁 → 🜂 → 🜄 → 🜆 → 🛡️")

    # External triggers
    root.after(100, lambda: on_mutation() if on_mutation else None)
    root.after(100, lambda: on_defense() if on_defense else None)

    # Expose feedback functions
    root.mutation_feedback = mutation_feedback
    root.defense_feedback = defense_feedback

    root.mainloop()

