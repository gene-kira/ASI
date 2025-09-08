# panels/swarm_map_panel.py

import tkinter as tk

class SwarmMapPanel(tk.Frame):
    def __init__(self, parent, swarm_nodes, font_size=10):
        super().__init__(parent, bg="#ffffff")
        self.font = ("Segoe UI", font_size)
        self.swarm_nodes = swarm_nodes

        title = tk.Label(self, text="🧭 Swarm Map", font=("Segoe UI", font_size + 2, "bold"), bg="#ffffff", fg="#333")
        title.pack(anchor="w", padx=10, pady=(10, 0))

        self.map_box = tk.Text(self, height=10, bg="#fefefe", font=self.font)
        self.map_box.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        self.update_map()

    def update_map(self):
        self.map_box.delete("1.0", tk.END)
        for iface, label in self.swarm_nodes.items():
            self.map_box.insert(tk.END, f"{iface} → {label} [🟢 Synced]\n")
        self.map_box.see(tk.END)

