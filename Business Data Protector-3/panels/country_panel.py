# panels/country_panel.py

import tkinter as tk
from tkinter import ttk
import requests
from utils import log_codex
from persona_engine import inject_persona
from deception_engine import trigger_deception_overlay

# Nested country config
country_regions = {
    "North America": {
        "USA": {"flag": "🇺🇸", "allow": True, "persona": "Sentinel"},
        "Canada": {"flag": "🇨🇦", "allow": True, "persona": "Guardian"},
        "Mexico": {"flag": "🇲🇽", "allow": False, "persona": "Echo"},
    },
    "Europe": {
        "Germany": {"flag": "🇩🇪", "allow": True, "persona": "Watcher"},
        "France": {"flag": "🇫🇷", "allow": True, "persona": "Pulse"},
        "UK": {"flag": "🇬🇧", "allow": False, "persona": "Shade"},
    },
    "Asia": {
        "Japan": {"flag": "🇯🇵", "allow": True, "persona": "Blade"},
        "India": {"flag": "🇮🇳", "allow": True, "persona": "Spark"},
        "China": {"flag": "🇨🇳", "allow": False, "persona": "Mirror"},
    },
    "Africa": {
        "Nigeria": {"flag": "🇳🇬", "allow": True, "persona": "Beacon"},
        "South Africa": {"flag": "🇿🇦", "allow": True, "persona": "Forge"},
    },
    "South America": {
        "Brazil": {"flag": "🇧🇷", "allow": True, "persona": "Pulse"},
        "Argentina": {"flag": "🇦🇷", "allow": False, "persona": "Veil"},
    }
}

def detect_country():
    try:
        res = requests.get("https://ipapi.co/json/")
        data = res.json()
        return data.get("country_name", "Unknown")
    except:
        return "Unknown"

class CountryPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#111")
        self.country_var = tk.StringVar()
        self.build_dropdown()
        self.country_var.trace("w", self.on_country_change)

    def build_dropdown(self):
        title = tk.Label(self, text="🌍 Country Selector", fg="#0ff", bg="#111", font=("Helvetica", 12))
        title.pack(pady=5)

        country_list = []
        self.country_map = {}  # Maps label → country name

        for region, countries in country_regions.items():
            for name, data in countries.items():
                label = f"{data['flag']} {name} ({region})"
                country_list.append(label)
                self.country_map[label] = name

        self.dropdown = ttk.Combobox(self, textvariable=self.country_var, values=country_list, state="readonly")
        self.dropdown.pack(pady=5)

        # Auto-detect and preselect
        detected = detect_country()
        for region, countries in country_regions.items():
            if detected in countries:
                flag = countries[detected]["flag"]
                label = f"{flag} {detected} ({region})"
                self.country_var.set(label)
                log_codex(f"🌐 Auto-detected country: {label}")
                break

    def on_country_change(self, *args):
        label = self.country_var.get()
        name = self.country_map.get(label)
        if not name:
            log_codex(f"⚠️ Unknown country label: {label}")
            return

        for region, countries in country_regions.items():
            if name in countries:
                config = countries[name]
                persona = config["persona"]
                if config["allow"]:
                    inject_persona(persona)
                    log_codex(f"✅ Country: {name} → Persona: {persona} | Access: Allowed")
                else:
                    trigger_deception_overlay(persona)
                    log_codex(f"🛡️ Country: {name} → Persona: {persona} | Access: Blocked → Deception triggered")

