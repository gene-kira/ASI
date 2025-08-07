import tkinter as tk
from tkinter import ttk, StringVar
import psutil
import shutil
from ram_cache import create_ramdisk
from gpu_fx_engine import trigger_fx

# GUI setup
root = tk.Tk()
root.title("Mythic RAM Cache")
root.geometry("400x300")
root.configure(bg="#0f0f1f")

# RAM slider
ttk.Label(root, text="RAM Cache Size", foreground="white", background="#0f0f1f").pack(pady=10)
ram_slider = ttk.Scale(root, from_=128, to=8192, orient="horizontal")
ram_slider.pack(fill="x", padx=20)

# Status label
status_label = ttk.Label(root, text="🌀 Cache Aura: Idle", foreground="cyan", background="#0f0f1f")
status_label.pack(pady=10)

# Telemetry display
stats_var = StringVar()
stats_label = ttk.Label(root, textvariable=stats_var, foreground="white", background="#0f0f1f")
stats_label.pack(pady=10)

def get_memory_stats():
    mem = psutil.virtual_memory()
    total_mb = mem.total // (1024 * 1024)
    used_mb = (mem.total - mem.available) // (1024 * 1024)
    percent_used = mem.percent
    return total_mb, used_mb, percent_used

def get_cache_usage(drive="R:"):
    try:
        total, used, free = shutil.disk_usage(drive)
        total_mb = total // (1024 * 1024)
        used_mb = used // (1024 * 1024)
        percent_full = (used / total) * 100
        return total_mb, used_mb, percent_full
    except:
        return 0, 0, 0

def update_stats():
    total, used, percent = get_memory_stats()
    cache_total, cache_used, cache_percent = get_cache_usage()
    stats_var.set(
        f"🧠 RAM: {used}/{total} MB ({percent}%)\n"
        f"🌀 Cache: {cache_used}/{cache_total} MB ({cache_percent:.1f}%)"
    )

    # FX triggers
    if percent > 90:
        trigger_fx("overload", percent)
        status_label.config(text="🔴 Cache Aura: Overloaded")
    elif cache_percent > 80:
        trigger_fx("purge", cache_percent)
        status_label.config(text="🟠 Cache Aura: Purging")
    else:
        status_label.config(text="🟢 Cache Aura: Stable")

    root.after(1000, update_stats)

def apply_settings():
    size = int(ram_slider.get())
    create_ramdisk(size)
    trigger_fx("allocate", size)
    status_label.config(text=f"🌀 Cache Aura: {size}MB Allocated")

ttk.Button(root, text="Apply", command=apply_settings).pack(pady=10)

update_stats()
root.mainloop()

