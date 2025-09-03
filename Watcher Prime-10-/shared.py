# shared.py — Shared Codex Vault + Display Utilities

# 📜 Symbolic memory stream
codex_vault = []

# 🧾 Log output to GUI or console
def log_output(message, log_widget=None):
    if log_widget:
        try:
            log_widget.insert("end", message + "\n")
            log_widget.see("end")
        except Exception:
            print(f"[GUI Log Error] {message}")
    else:
        print(message)

# 📂 Update Codex Vault display (optional-safe)
def update_codex_display(codex_widget=None):
    if not codex_widget:
        return  # No widget passed—skip GUI update
    try:
        codex_widget.delete(0, "end")
        for entry in codex_vault[-50:]:
            codex_widget.insert("end", f"{entry['timestamp']} | {entry['source']} | {entry['status']}")
    except Exception as e:
        print(f"[Codex Display Error] {e}")

