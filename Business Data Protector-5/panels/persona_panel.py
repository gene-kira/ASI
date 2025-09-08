# panels/persona_panel.py

import tkinter as tk

class PersonaPanel(tk.Frame):
    def __init__(self, parent, font_size=12):
        super().__init__(parent, bg="#111")
        self.font = ("Helvetica", font_size)

        title = tk.Label(self, text="🎭 Persona", fg="#0ff", bg="#111", font=self.font)
        title.pack(pady=5)

        self.persona_label = tk.Label(self, text="Persona: Unknown", fg="#0f0", bg="#111", font=self.font)
        self.persona_label.pack(pady=2)

    def set_persona(self, persona):
        self.persona_label.config(text=f"Persona: {persona}")

