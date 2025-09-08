# panels/swarm_panel.py

import tkinter as tk

class SwarmPanel(tk.Frame):
    def __init__(self, parent, iface_map):
        super().__init__(parent, bg="#111")
        self.labels = {}

        title = tk.Label(self, text="🧠 Swarm Sync Panel", fg="#0ff", bg="#111", font=("Helvetica", 12))
        title.pack(pady=5)

        for iface, label_text in iface_map.items():
            frame = tk.Frame(self, bg="#111")
            frame.pack(fill=tk.X, padx=10, pady=2)

            label = tk.Label(frame, text=label_text, fg="#0ff", bg="#111", width=30, anchor="w")
            label.pack(side=tk.LEFT)

            status = tk.Label(frame, text="Checking...", fg="#888", bg="#111", anchor="w")
            status.pack(side=tk.LEFT, fill=tk.X, expand=True)

            self.labels[iface] = status
            print(f"🧠 Initialized label for {iface}: {label_text}")

    def update_sync(self, iface, status):
        print(f"🧪 update_sync called for {iface} → {status}")
        if iface in self.labels:
            print(f"✅ Label found for {iface}, updating...")
            self.labels[iface].after(0, lambda: self.labels[iface].config(text=status))
        else:
            print(f"❌ Label NOT found for {iface}")

