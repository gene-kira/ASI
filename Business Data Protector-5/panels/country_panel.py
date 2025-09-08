# panels/country_panel.py

import tkinter as tk
from utils import log_codex

# Shared blocklist dictionary
blocked_countries = {
    "Russia": True,
    "China": True,
    "North Korea": True,
    "Iran": True
}

class CountryPanel(tk.Frame):
    def __init__(self, parent, font_size=10):
        super().__init__(parent, bg="#111")
        self.font = ("Helvetica", font_size)
        self.current_country = "Unknown"

        # Title
        title = tk.Label(self, text="🌍 Country Access Control", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        # Detected country label
        self.country_label = tk.Label(self, text="Detected: Unknown", fg="#0f0", bg="#111", font=self.font)
        self.country_label.pack(pady=2)

        # Manual entry
        self.country_entry = tk.Entry(self, font=self.font, width=20)
        self.country_entry.pack(pady=5)

        # Dropdown selector
        self.country_selector = tk.StringVar()
        country_list = sorted(blocked_countries.keys()) or ["Unknown"]
        self.dropdown = tk.OptionMenu(self, self.country_selector, *country_list)
        self.dropdown.config(font=self.font)
        self.dropdown.pack(pady=5)

        # Buttons
        btn_frame = tk.Frame(self, bg="#111")
        btn_frame.pack(pady=5)

        allow_btn = tk.Button(btn_frame, text="Allow Country", command=self.allow_country, font=self.font)
        allow_btn.pack(side=tk.LEFT, padx=5)

        block_btn = tk.Button(btn_frame, text="Block Country", command=self.block_country, font=self.font)
        block_btn.pack(side=tk.LEFT, padx=5)

    def set_country(self, country):
        self.current_country = country
        self.country_label.config(text=f"Detected: {country}")

    def allow_country(self):
        country = self.country_entry.get() or self.country_selector.get()
        if country:
            blocked_countries[country] = False
            log_codex(f"✅ Country allowed: {country}")
            self.country_label.config(text=f"Allowed: {country}", fg="#0f0")

    def block_country(self):
        country = self.country_entry.get() or self.country_selector.get()
        if country:
            blocked_countries[country] = True
            log_codex(f"🚫 Country blocked: {country}")
            self.country_label.config(text=f"Blocked: {country}", fg="#f00")

