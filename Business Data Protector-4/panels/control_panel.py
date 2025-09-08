# panels/control_panel.py

import tkinter as tk
from utils import save_memory, log_codex

class ControlPanel(tk.Frame):
    def __init__(self, parent, memory):
        super().__init__(parent, bg="#222")
        self.memory = memory

        tk.Label(self, text="🛡️ Control Panel", fg="#0ff", bg="#222", font=("Helvetica", 12)).pack(pady=5)

        btn_frame = tk.Frame(self, bg="#222")
        btn_frame.pack()

        tk.Button(btn_frame, text="🔐 Allow / Block", command=self.open_allow_block).pack(side=tk.LEFT, padx=10)
        tk.Button(btn_frame, text="🌍 Country Filter", command=self.open_country_filter).pack(side=tk.LEFT, padx=10)

    def open_allow_block(self):
        win = tk.Toplevel(self)
        win.title("🔐 Allow / Block Entities")
        win.geometry("400x500")
        win.configure(bg="#222")

        tk.Label(win, text="Allowed Entities", fg="#0f0", bg="#222").pack(pady=5)
        allow_box = tk.Listbox(win, bg="#111", fg="#0f0")
        allow_box.pack(fill=tk.BOTH, expand=True, padx=10)

        tk.Label(win, text="Blocked Entities", fg="#f00", bg="#222").pack(pady=5)
        block_box = tk.Listbox(win, bg="#111", fg="#f00")
        block_box.pack(fill=tk.BOTH, expand=True, padx=10)

        for item in self.memory.get("allowed", []):
            allow_box.insert(tk.END, item)
        for item in self.memory.get("blocked", []):
            block_box.insert(tk.END, item)

        entry = tk.Entry(win, bg="#111", fg="#0ff")
        entry.pack(pady=5, fill=tk.X, padx=10)

        tk.Button(win, text="Add to Allowed", command=lambda: self.add_entity(entry.get(), allow_box, "allowed")).pack(pady=2)
        tk.Button(win, text="Add to Blocked", command=lambda: self.add_entity(entry.get(), block_box, "blocked")).pack(pady=2)
        tk.Button(win, text="Toggle Selection", command=lambda: self.toggle_entity(allow_box, block_box)).pack(pady=10)

    def add_entity(self, value, box, category):
        if value and value not in self.memory[category]:
            self.memory[category].append(value)
            save_memory(self.memory)
            box.insert(tk.END, value)
            log_codex(f"➕ Added to {category}: {value}")

    def toggle_entity(self, allow_box, block_box):
        selected = allow_box.curselection()
        if selected:
            item = allow_box.get(selected[0])
            allow_box.delete(selected[0])
            block_box.insert(tk.END, item)
            self.memory["allowed"].remove(item)
            self.memory["blocked"].append(item)
            save_memory(self.memory)
            log_codex(f"🚫 Blocked: {item}")
        else:
            selected = block_box.curselection()
            if selected:
                item = block_box.get(selected[0])
                block_box.delete(selected[0])
                allow_box.insert(tk.END, item)
                self.memory["blocked"].remove(item)
                self.memory["allowed"].append(item)
                save_memory(self.memory)
                log_codex(f"✅ Allowed: {item}")

    def open_country_filter(self):
        win = tk.Toplevel(self)
        win.title("🌍 Country Filter")
        win.geometry("400x300")
        win.configure(bg="#222")

        tk.Label(win, text="Detected Countries", fg="#0ff", bg="#222").pack(pady=5)
        country_box = tk.Listbox(win, bg="#111", fg="#0ff")
        country_box.pack(fill=tk.BOTH, expand=True, padx=10)

        countries = ["United States", "Germany", "China", "Brazil", "Russia"]
        blocked = self.memory.get("countries_blocked", [])
        for c in countries:
            label = f"{c} (BLOCKED)" if c in blocked else c
            country_box.insert(tk.END, label)

        tk.Button(win, text="Block Selected", command=lambda: self.block_country(country_box)).pack(pady=10)

    def block_country(self, box):
        selected = box.curselection()
        if selected:
            country = box.get(selected[0]).split(" ")[0]
            if country not in self.memory["countries_blocked"]:
                self.memory["countries_blocked"].append(country)
                save_memory(self.memory)
                log_codex(f"🌍 Country blocked: {country}")

