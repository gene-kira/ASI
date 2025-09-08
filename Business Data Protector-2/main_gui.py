# main_gui.py

import tkinter as tk
import psutil
from utils import load_memory, log_codex

# Panels
from panels.status_panel import StatusPanel
from panels.persona_panel import PersonaPanel
from panels.swarm_panel import SwarmPanel
from panels.codex_panel import CodexPanel
from panels.control_panel import ControlPanel
from panels.overlay_panel import OverlayPanel
from panels.threat_matrix_panel import ThreatMatrixPanel
from panels.codex_dashboard_panel import CodexDashboardPanel
from panels.country_panel import CountryPanel  # NEW: Region-aware selector

class MythicNodeGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("🌀 MythicNode ASI Interface")
        self.geometry("1200x800")
        self.configure(bg="#222")

        # Load persistent memory
        self.memory = load_memory()

        # Discover network interfaces
        self.swarm_nodes = self.discover_interfaces()  # Dict: {iface: "Label (IP)"}

        # Panels
        self.status_panel = StatusPanel(self)
        self.status_panel.pack(fill=tk.X, pady=5)

        self.persona_panel = PersonaPanel(self)
        self.persona_panel.pack(fill=tk.X, pady=5)

        self.country_panel = CountryPanel(self)  # 🌍 Region-aware selector
        self.country_panel.pack(fill=tk.X, pady=5)

        self.swarm_panel = SwarmPanel(self, self.swarm_nodes)
        self.swarm_panel.pack(fill=tk.X, pady=5)

        self.codex_panel = CodexPanel(self)
        self.codex_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        self.control_panel = ControlPanel(self, self.memory)
        self.control_panel.pack(fill=tk.X, pady=5)

        self.overlay_panel = OverlayPanel(self)
        self.overlay_panel.pack(fill=tk.X, pady=5)

        self.threat_matrix_panel = ThreatMatrixPanel(self, self.memory)
        self.threat_matrix_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        self.codex_dashboard_panel = CodexDashboardPanel(self)
        self.codex_dashboard_panel.pack(fill=tk.BOTH, expand=True, pady=5)

    def discover_interfaces(self):
        nodes = {}
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family.name == "AF_INET" and not addr.address.startswith("127."):
                    label = f"{iface} ({addr.address})"
                    nodes[iface] = label
                    log_codex(f"🔍 Interface discovered: {label}")
        return nodes

