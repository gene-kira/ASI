# main_gui.py

import tkinter as tk
import psutil
from utils import load_memory, log_codex

# Panels
from panels.status_panel import StatusPanel
from panels.persona_panel import PersonaPanel
from panels.country_panel import CountryPanel
from panels.swarm_panel import SwarmPanel
from panels.control_panel import ControlPanel
from panels.overlay_panel import OverlayPanel
from panels.threat_matrix_panel import ThreatMatrixPanel
from panels.codex_dashboard_panel import CodexDashboardPanel

class MythicNodeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌀 MythicNode ASI Interface")
        self.geometry("700x500")  # Compact layout

        # Center the window on screen
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w // 2) - (700 // 2)
        y = (screen_h // 2) - (500 // 2)
        self.geometry(f"700x500+{x}+{y}")

        self.configure(bg="#222")
        self.memory = load_memory()
        self.swarm_nodes = self.discover_interfaces()  # Dict: {iface: "Label (IP)"}

        # Panels
        self.status_panel = StatusPanel(self)
        self.status_panel.pack(fill=tk.X, pady=2)

        self.persona_panel = PersonaPanel(self)
        self.persona_panel.pack(fill=tk.X, pady=2)

        self.country_panel = CountryPanel(self)
        self.country_panel.pack(fill=tk.X, pady=2)

        self.swarm_panel = SwarmPanel(self, self.swarm_nodes)
        self.swarm_panel.pack(fill=tk.X, pady=2)

        self.control_panel = ControlPanel(self, self.memory)
        self.control_panel.pack(fill=tk.X, pady=2)

        self.overlay_panel = OverlayPanel(self)
        self.overlay_panel.pack(fill=tk.X, pady=2)

        self.threat_matrix_panel = ThreatMatrixPanel(self, self.memory)
        self.threat_matrix_panel.pack(fill=tk.BOTH, expand=True, pady=2)

        self.codex_dashboard_panel = CodexDashboardPanel(self)
        self.codex_dashboard_panel.pack(fill=tk.BOTH, expand=True, pady=2)

    def discover_interfaces(self):
        nodes = {}
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family.name == "AF_INET" and not addr.address.startswith("127."):
                    label = f"{iface} ({addr.address})"
                    nodes[iface] = label
                    log_codex(f"🔍 Interface discovered: {label}")
        return nodes

