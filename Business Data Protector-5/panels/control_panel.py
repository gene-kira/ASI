# panels/control_panel.py

import tkinter as tk
from utils import log_codex
from ip_blocker import block_ip_temporary, unblock_ip

class ControlPanel(tk.Frame):
    def __init__(self, parent, memory, font_size=10):
        super().__init__(parent, bg="#111")
        self.font = ("Helvetica", font_size)
        self.memory = memory

        # Title
        title = tk.Label(self, text="🧠 IP Control Panel", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        # Memory count
        self.memory_label = tk.Label(self, text=f"Memory: {len(memory)} entries", fg="#0f0", bg="#111", font=self.font)
        self.memory_label.pack(pady=2)

        # IP entry + dropdown
        ip_frame = tk.Frame(self, bg="#111")
        ip_frame.pack(pady=5)

        self.ip_entry = tk.Entry(ip_frame, font=self.font, width=20)
        self.ip_entry.pack(side=tk.LEFT, padx=5)

        self.ip_selector = tk.StringVar()
        ip_list = self.get_recent_ips() or ["0.0.0.0"]
        self.ip_selector.set(ip_list[0])
        self.ip_dropdown = tk.OptionMenu(ip_frame, self.ip_selector, *ip_list)
        self.ip_dropdown.config(font=self.font)
        self.ip_dropdown.pack(side=tk.LEFT, padx=5)

        # Buttons
        btn_frame = tk.Frame(self, bg="#111")
        btn_frame.pack(pady=5)

        allow_btn = tk.Button(btn_frame, text="Allow IP", command=self.allow_ip, font=self.font)
        allow_btn.pack(side=tk.LEFT, padx=5)

        block_btn = tk.Button(btn_frame, text="Block IP", command=self.block_ip, font=self.font)
        block_btn.pack(side=tk.LEFT, padx=5)

    def update_memory_count(self, count):
        self.memory_label.config(text=f"Memory: {count} entries")

    def get_recent_ips(self):
        return [entry.get("ip", "0.0.0.0") for entry in self.memory if "ip" in entry]

    def allow_ip(self):
        ip = self.ip_entry.get() or self.ip_selector.get()
        if ip:
            unblock_ip(ip)
            log_codex(f"✅ IP allowed: {ip}")

    def block_ip(self):
        ip = self.ip_entry.get() or self.ip_selector.get()
        if ip:
            block_ip_temporary(ip, duration=3600)
            log_codex(f"🚫 IP blocked: {ip}")

