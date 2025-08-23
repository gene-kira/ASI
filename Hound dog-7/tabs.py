# tabs.py
import tkinter as tk
from tkinter import ttk

def create_tabs(app, notebook):
    app.watchtower_tab = ttk.Frame(notebook)
    app.ip_tracker_tab = ttk.Frame(notebook)
    app.threat_tab = ttk.Frame(notebook)
    app.voice_tab = ttk.Frame(notebook)
    app.config_tab = ttk.Frame(notebook)
    app.mutation_tab = ttk.Frame(notebook)
    app.glyph_tab = ttk.Frame(notebook)

    notebook.add(app.watchtower_tab, text="🕵️ Process Watchtower")
    notebook.add(app.ip_tracker_tab, text="🌐 Foreign IP Tracker")
    notebook.add(app.threat_tab, text="🔥 Threat Response")
    notebook.add(app.voice_tab, text="🗣️ Voice Feedback")
    notebook.add(app.config_tab, text="⚙️ Config Panel")
    notebook.add(app.mutation_tab, text="🧬 Mutation Trails")
    notebook.add(app.glyph_tab, text="🧠 GlyphCanvas")

