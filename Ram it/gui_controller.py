import tkinter as tk
from tkinter import ttk
from ram_cache import create_ramdisk
from gpu_fx_engine import trigger_fx

def apply_settings():
    size = int(ram_slider.get())
    create_ramdisk(size)
    status_label.config(text=f"🌀 Cache Aura: {size}MB Allocated")
    trigger_fx("allocate", size)

root = tk.Tk()
root.title("Mythic RAM Cache")

ttk.Label(root, text="RAM Cache Size").pack(pady=10)
ram_slider = ttk.Scale(root, from_=128, to=8192, orient="horizontal")
ram_slider.pack(fill="x", padx=20)

ttk.Button(root, text="Apply", command=apply_settings).pack(pady=10)
status_label = ttk.Label(root, text="🌀 Cache Aura: Idle")
status_label.pack(pady=10)

root.mainloop()

