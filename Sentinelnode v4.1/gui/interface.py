import tkinter as tk
from tkinter import scrolledtext
import threading
from core.node import SentinelNode
from core.autonomous import autonomous_ingest
from modules.narrator import MythicNarrator

class MythicDefenseGUI:
    def __init__(self, root):
        root.title("SentinelNode v4.1")
        root.geometry("600x350")
        root.configure(bg="#1a1a1a")

        self.log_area = scrolledtext.ScrolledText(root, bg="#000", fg="#0f0", font=("Consolas", 9))
        self.log_area.place(x=10, y=10, width=580, height=300)

        self.narrator = MythicNarrator(self.log_area)
        self.node = SentinelNode(self.narrator)

        self.control_panel(root)
        threading.Thread(target=autonomous_ingest, args=(self.node,), daemon=True).start()

    def control_panel(self, root):
        panel = tk.Frame(root, bg="#333")
        panel.place(x=10, y=310, width=580, height=30)

        def add_ip():
            ip = "192.168.1.200"
            self.node.ip_control.allow_list.add(ip)
            self.narrator.log(f"IP {ip} added to allow list")

        def block_ip():
            ip = "203.0.113.99"
            self.node.ip_control.block_list.add(ip)
            self.narrator.log(f"IP {ip} added to block list")

        def show_ips():
            allow = ", ".join(self.node.ip_control.allow_list)
            block = ", ".join(self.node.ip_control.block_list)
            self.narrator.log(f"Allow List: {allow}")
            self.narrator.log(f"Block List: {block}")

        def inject_telemetry():
            self.node.telemetry.inject()

        def purge_all():
            self.node.destructor.tracked.clear()
            self.narrator.warn("All tracked data purged manually")

        tk.Button(panel, text="Add IP", command=add_ip, bg="#444", fg="#fff", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(panel, text="Block IP", command=block_ip, bg="#600", fg="#fff", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(panel, text="Show IPs", command=show_ips, bg="#222", fg="#0f0", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(panel, text="Inject Telemetry", command=inject_telemetry, bg="#444", fg="#fff", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)
        tk.Button(panel, text="Purge All", command=purge_all, bg="#800", fg="#fff", font=("Arial", 8)).pack(side=tk.LEFT, padx=5)

