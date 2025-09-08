# panels/persona_panel.py

import tkinter as tk
from persona import personas

class PersonaPanel(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent, bg="#222")
        self.active_persona = tk.StringVar(value="None")
        self.overlay_label = tk.Label(self, text="🧬 Persona: None", fg="#888", bg="#222", font=("Helvetica", 12))
        self.overlay_label.pack(pady=5)

    def set_persona(self, name):
        data = personas.get(name)
        if data:
            self.active_persona.set(name)
            self.overlay_label.config(text=f"{data['overlay']} Persona: {name}", fg=data["color"])
        else:
            self.active_persona.set("None")
            self.overlay_label.config(text="🧬 Persona: None", fg="#888")

