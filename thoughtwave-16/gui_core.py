import tkinter as tk

BG_COLOR = "#1e1e2f"
BTN_COLOR = "#5cdb95"
TEXT_COLOR = "#ffffff"
FONT = ("Segoe UI", 12)

def setup_gui():
    root = tk.Tk()
    root.title("MagicBox ASI Mixer")
    root.configure(bg=BG_COLOR)
    root.geometry("500x700")

    labels = {}
    labels["status"] = tk.Label(root, text="ASI Status: Dormant", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
    labels["status"].pack(pady=4)

    labels["thought"] = tk.Label(
        root,
        text="Awaiting cognition...",
        bg=BG_COLOR,
        fg=TEXT_COLOR,
        font=("Consolas", 10),
        wraplength=480,
        justify="left",
        height=8
    )
    labels["thought"].pack(pady=8)

    memory_list = tk.Listbox(root, bg=BG_COLOR, fg=TEXT_COLOR, font=("Consolas", 10), width=60, height=6)
    memory_list.pack(pady=6)

    consensus_list = tk.Listbox(root, bg=BG_COLOR, fg="#00ffcc", font=("Consolas", 10), width=60, height=3)
    consensus_list.pack(pady=4)

    drive_label = tk.Label(root, text="Storage Drive: [Auto]", bg=BG_COLOR, fg="#00ffcc", font=FONT)
    drive_label.pack(pady=4)

    drive_button = tk.Button(root, text="Select Primary Drive", bg=BTN_COLOR, fg=BG_COLOR, font=FONT)
    drive_button.pack(pady=4)

    backup_label = tk.Label(root, text="Backup Drive: [None]", bg=BG_COLOR, fg="#ffcc00", font=FONT)
    backup_label.pack(pady=4)

    backup_button = tk.Button(root, text="Select Backup Drive", bg=BTN_COLOR, fg=BG_COLOR, font=FONT)
    backup_button.pack(pady=4)

    return root, labels, memory_list, consensus_list, drive_label, drive_button, backup_label, backup_button

