# main_gui.py

import tkinter as tk
import psutil
from utils import load_memory, log_codex
from panels.status_panel import StatusPanel
from panels.persona_panel import PersonaPanel
from panels.country_panel import CountryPanel
from panels.swarm_panel import SwarmPanel
from panels.control_panel import ControlPanel
from panels.overlay_panel import OverlayPanel
from panels.threat_matrix_panel import ThreatMatrixPanel
from panels.codex_dashboard_panel import CodexDashboardPanel
from panels.traffic_monitor_panel import TrafficMonitorPanel

def get_scaled_font(base_size=12, min_size=6):
    root = tk.Tk()
    dpi = root.winfo_fpixels('1i')
    root.destroy()
    scale = dpi / 96
    scaled = int(base_size * scale * 0.5)
    return max(scaled, min_size)

class MythicNodeGUI:
    def __init__(self, TkEngine):
        self.root = TkEngine()
        self.root.title("🌀 MythicNode ASI Interface")
        self.root.geometry("900x600")
        self.root.configure(bg="#eaeaea")

        self.memory = load_memory()
        self.swarm_nodes = self.discover_interfaces()

        top_bar = tk.Frame(self.root, bg="#333")
        top_bar.pack(fill=tk.X)
        title = tk.Label(top_bar, text="MythicNode Dashboard", fg="#fff", bg="#333", font=("Helvetica", get_scaled_font(16)))
        title.pack(padx=10, pady=10)

        container = tk.Frame(self.root, bg="#eaeaea")
        container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        left = tk.LabelFrame(container, text="System Status", bg="#f8f8f8", font=("Helvetica", get_scaled_font(12)))
        left.grid(row=0, column=0, sticky="nsew", padx=10, pady=10)

        self.status_panel = StatusPanel(left, font_size=get_scaled_font(6))
        self.status_panel.pack(fill=tk.X, pady=5)

        self.persona_panel = PersonaPanel(left, font_size=get_scaled_font(6))
        self.persona_panel.pack(fill=tk.X, pady=5)

        self.country_panel = CountryPanel(left, font_size=get_scaled_font(6))
        self.country_panel.pack(fill=tk.X, pady=5)

        self.swarm_panel = SwarmPanel(left, self.swarm_nodes, font_size=get_scaled_font(6))
        self.swarm_panel.pack(fill=tk.X, pady=5)

        right = tk.LabelFrame(container, text="Control & Intelligence", bg="#f8f8f8", font=("Helvetica", get_scaled_font(12)))
        right.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.control_panel = ControlPanel(right, self.memory, font_size=get_scaled_font(6))
        self.control_panel.pack(fill=tk.X, pady=5)

        self.overlay_panel = OverlayPanel(right, font_size=get_scaled_font(6))
        self.overlay_panel.pack(fill=tk.X, pady=5)

        self.threat_matrix_panel = ThreatMatrixPanel(right, self.memory, font_size=get_scaled_font(6))
        self.threat_matrix_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        self.codex_dashboard_panel = CodexDashboardPanel(right, font_size=get_scaled_font(6))
        self.codex_dashboard_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        self.traffic_monitor_panel = TrafficMonitorPanel(right, font_size=get_scaled_font(6))
        self.traffic_monitor_panel.pack(fill=tk.BOTH, expand=True, pady=5)

        container.grid_columnconfigure(0, weight=1)
        container.grid_columnconfigure(1, weight=2)

    def discover_interfaces(self):
        nodes = {}
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family.name == "AF_INET" and not addr.address.startswith("127."):
                    label = f"{iface} ({addr.address})"
                    nodes[iface] = label
                    log_codex(f"🔍 Interface discovered: {label}")
        return nodes

