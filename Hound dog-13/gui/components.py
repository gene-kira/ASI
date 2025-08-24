# components.py
import tkinter as tk
from tkinter import ttk
from config import MAGICBOX_COLORS
from voice import speak

def build_text_panel(parent, label_text):
    label = tk.Label(parent, text=label_text, bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
    label.pack(fill=tk.X)
    text = tk.Text(parent, bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Courier", 12))
    text.pack(expand=True, fill=tk.BOTH)
    return text

def build_voice_panel(parent):
    label = tk.Label(parent, text="Voice Feedback Settings", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
    label.pack(fill=tk.X)
    test_btn = ttk.Button(parent, text="Test Voice", command=lambda: speak("Voice system online. Ready to defend."))
    test_btn.pack(pady=10)

def build_config_panel(parent, trust_threshold, update_callback):
    label = tk.Label(parent, text="Trust Rules & Kill Thresholds", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"], font=("Helvetica", 14))
    label.pack(fill=tk.X)
    slider = ttk.Scale(parent, from_=1, to=10, orient="horizontal", command=update_callback)
    slider.set(trust_threshold)
    slider.pack(pady=20)
    threshold_label = tk.Label(parent, text=f"Kill Threshold: {trust_threshold}", bg=MAGICBOX_COLORS["panel"], fg=MAGICBOX_COLORS["fg"])
    threshold_label.pack()
    return slider, threshold_label

