# panels/status_panel.py

import tkinter as tk

class StatusPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#222")

        self.health_var = tk.StringVar(value="Scanning...")
        self.ports_var = tk.StringVar(value="Loading...")
        self.enhancer_var = tk.StringVar(value="Idle")
        self.emergency_var = tk.StringVar(value="None")

        self._build_ui()

    def _build_ui(self):
        title = tk.Label(self, text="🧠 System Status", fg="#0ff", bg="#222", font=("Helvetica", 12))
        title.grid(row=0, column=0, columnspan=2, sticky="w", padx=10, pady=(5, 10))

        labels = [
            ("PDP Health:", self.health_var),
            ("Active Ports:", self.ports_var),
            ("Auto-Enhancer:", self.enhancer_var),
            ("Emergency Status:", self.emergency_var)
        ]

        for i, (label_text, var) in enumerate(labels, start=1):
            tk.Label(self, text=label_text, fg="#0ff", bg="#222").grid(row=i, column=0, sticky="w", padx=10)
            tk.Label(self, textvariable=var, fg="#0ff", bg="#222").grid(row=i, column=1, sticky="w")

    def update_health(self, status, emergency=None):
        self.health_var.set(status)
        if emergency:
            self.emergency_var.set(emergency)
        else:
            self.emergency_var.set("None")

    def update_ports(self, port_list):
        if port_list:
            self.ports_var.set(", ".join(str(p) for p in port_list))
        else:
            self.ports_var.set("None")

    def update_enhancer(self, status):
        self.enhancer_var.set(status)

