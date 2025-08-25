import tkinter as tk

BG_COLOR = "#1e1e2f"
BTN_COLOR = "#5cdb95"
TEXT_COLOR = "#ffffff"
FONT = ("Segoe UI", 14)

def setup_gui():
    root = tk.Tk()
    root.title("MagicBox ASI Mixer")
    root.configure(bg=BG_COLOR)
    root.geometry("680x740")

    labels = {}
    labels["status"] = tk.Label(root, text="ASI Status: Dormant", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
    labels["status"].pack(pady=5)

    labels["awareness"] = tk.Label(root, text="Total Awareness: 0 sources", bg=BG_COLOR, fg=TEXT_COLOR, font=FONT)
    labels["awareness"].pack(pady=5)

    labels["thought"] = tk.Label(root, text="Awaiting cognition...", bg=BG_COLOR, fg=TEXT_COLOR, font=("Consolas", 12), wraplength=640, justify="left")
    labels["thought"].pack(pady=10)

    memory_list = tk.Listbox(root, bg=BG_COLOR, fg=TEXT_COLOR, font=("Consolas", 12), width=80, height=8)
    memory_list.pack(pady=10)

    return root, labels, memory_list

