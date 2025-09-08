# main_gui.py

import tkinter as tk
import psutil
from utils import load_memory
from panels.status_panel import StatusPanel
from panels.persona_panel import PersonaPanel
from panels.country_panel import CountryPanel
from panels.swarm_panel import SwarmPanel
from panels.control_panel import ControlPanel
from panels.overlay_panel import OverlayPanel
from panels.threat_matrix_panel import ThreatMatrixPanel
from panels.codex_dashboard_panel import CodexDashboardPanel
from panels.traffic_monitor_panel import TrafficMonitorPanel
from panels.swarm_map_panel import SwarmMapPanel

class MythicNodeGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("MythicNode Control Center")
        self.root.geometry("1200x750")
        self.root.configure(bg="#f4f6f9")

        self.memory = load_memory()
        self.swarm_nodes = self.discover_interfaces()

        # Sidebar navigation
        sidebar = tk.Frame(self.root, bg="#2c3e50", width=180)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(sidebar, text="🛡️ MythicNode", fg="#ecf0f1", bg="#2c3e50", font=("Segoe UI", 14, "bold")).pack(pady=20)

        nav_buttons = [
            ("System", "System Overview"),
            ("Control", "Control & Intelligence"),
            ("Threats", "Threat Matrix"),
            ("Codex", "Codex Dashboard"),
            ("Traffic", "Traffic Monitor"),
            ("Swarm", "Swarm Map")
        ]

        self.tabs = {}

        for name, label in nav_buttons:
            btn = tk.Button(sidebar, text=label, fg="#ecf0f1", bg="#34495e", font=("Segoe UI", 10), relief=tk.FLAT,
                            command=lambda n=name: self.show_tab(n))
            btn.pack(fill=tk.X, padx=10, pady=5)

        self.content = tk.Frame(self.root, bg="#f4f6f9")
        self.content.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Build all tabs
        self.tabs["System"] = self.build_system_tab()
        self.tabs["Control"] = self.build_control_tab()
        self.tabs["Threats"] = self.build_threat_tab()
        self.tabs["Codex"] = self.build_codex_tab()
        self.tabs["Traffic"] = self.build_traffic_tab()
        self.tabs["Swarm"] = self.build_swarm_tab()

        self.show_tab("System")

    def show_tab(self, name):
        for tab in self.tabs.values():
            tab.pack_forget()
        self.tabs[name].pack(fill=tk.BOTH, expand=True)

    def build_system_tab(self):
        frame = tk.Frame(self.content, bg="#ffffff")
        tk.Label(frame, text="System Overview", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=20, pady=10)

        self.status_panel = StatusPanel(frame, font_size=10)
        self.status_panel.pack(fill=tk.X, padx=20, pady=5)

        self.persona_panel = PersonaPanel(frame, font_size=10)
        self.persona_panel.pack(fill=tk.X, padx=20, pady=5)

        self.country_panel = CountryPanel(frame, font_size=10)
        self.country_panel.pack(fill=tk.X, padx=20, pady=5)

        self.swarm_panel = SwarmPanel(frame, self.swarm_nodes, font_size=10)
        self.swarm_panel.pack(fill=tk.X, padx=20, pady=5)

        return frame

    def build_control_tab(self):
        frame = tk.Frame(self.content, bg="#ffffff")
        tk.Label(frame, text="Control & Intelligence", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=20, pady=10)

        self.control_panel = ControlPanel(frame, self.memory, font_size=10)
        self.control_panel.pack(fill=tk.X, padx=20, pady=5)

        self.overlay_panel = OverlayPanel(frame, font_size=10)
        self.overlay_panel.pack(fill=tk.X, padx=20, pady=5)

        return frame

    def build_threat_tab(self):
        frame = tk.Frame(self.content, bg="#ffffff")
        tk.Label(frame, text="Threat Matrix", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=20, pady=10)

        self.threat_matrix_panel = ThreatMatrixPanel(frame, self.memory, font_size=10)
        self.threat_matrix_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        return frame

    def build_codex_tab(self):
        frame = tk.Frame(self.content, bg="#ffffff")
        tk.Label(frame, text="Codex Dashboard", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=20, pady=10)

        self.codex_dashboard_panel = CodexDashboardPanel(frame, font_size=10)
        self.codex_dashboard_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        return frame

    def build_traffic_tab(self):
        frame = tk.Frame(self.content, bg="#ffffff")
        tk.Label(frame, text="Traffic Monitor", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=20, pady=10)

        self.traffic_monitor_panel = TrafficMonitorPanel(frame, font_size=10)
        self.traffic_monitor_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        return frame

    def build_swarm_tab(self):
        frame = tk.Frame(self.content, bg="#ffffff")
        tk.Label(frame, text="Swarm Map", font=("Segoe UI", 12, "bold"), bg="#ffffff").pack(anchor="w", padx=20, pady=10)

        self.swarm_map_panel = SwarmMapPanel(frame, self.swarm_nodes, font_size=10)
        self.swarm_map_panel.pack(fill=tk.BOTH, expand=True, padx=20, pady=5)

        return frame

    def discover_interfaces(self):
        nodes = {}
        for iface, addrs in psutil.net_if_addrs().items():
            for addr in addrs:
                if addr.family.name == "AF_INET" and not addr.address.startswith("127."):
                    label = f"{iface} ({addr.address})"
                    nodes[iface] = label
        return nodes

