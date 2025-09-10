# mythic_gui.py

import tkinter as tk
from tkinter import ttk

class MythicDefenseGUI(tk.Tk):
    def __init__(self, node_id="Node-Ω"):
        super().__init__()
        self.title(f"Mythic Defense {node_id}")
        self.geometry("1100x700")
        self.configure(bg="#f4f4f4")
        self.node_id = node_id
        self.audit_enabled = tk.BooleanVar(value=True)
        self.create_layout()

    def create_layout(self):
        # Panel: Ingest Monitor
        self.panel_ingest = self.create_panel("Ingest Monitor", 0, 0)
        self.ingest_log = self.create_log_area(self.panel_ingest)

        # Panel: Threat Matrix
        self.panel_threat = self.create_panel("Threat Matrix", 0, 1)
        self.threat_log = self.create_log_area(self.panel_threat)

        # Panel: Audit Controls
        self.panel_audit = self.create_panel("Audit Controls", 1, 0)
        ttk.Checkbutton(self.panel_audit, text="Enable Audit Mode", variable=self.audit_enabled).pack(pady=10)

        # Panel: Country Filter
        self.panel_country = self.create_panel("Country Filter", 1, 1)
        self.country_filter = tk.Entry(self.panel_country)
        self.country_filter.insert(0, "US,CA,UK")
        self.country_filter.pack(pady=10)

        # Panel: Persona Injection
        self.panel_persona = self.create_panel("Persona Injection", 2, 0)
        self.persona_status = ttk.Label(self.panel_persona, text="Persona: Dormant", foreground="gray")
        self.persona_status.pack(pady=10)

        # Panel: Event Bus
        self.panel_eventbus = self.create_panel("Event Bus", 2, 1)
        self.event_log = self.create_log_area(self.panel_eventbus)

    def create_panel(self, title, row, col):
        frame = ttk.LabelFrame(self, text=title, padding=10)
        frame.grid(row=row, column=col, padx=10, pady=10, sticky="nsew")
        return frame

    def create_log_area(self, parent):
        log = tk.Text(parent, height=10, width=50, bg="#ffffff", fg="#333333", font=("Consolas", 9))
        log.pack()
        return log

