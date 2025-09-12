# 🧬 DominionDeck: Mythic Windows 11 Control Codex
# Author: killer666 + Copilot
# Description: GUI launcher with elevation, autoloader, registry toggles, and symbolic feedback

import sys
import ctypes
import tkinter as tk
from tkinter import messagebox
import winreg

# 🔐 Elevation Check
def ensure_elevation():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False
    if not is_admin:
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

ensure_elevation()

# 📦 Autoloader (basic check)
required_modules = ['ctypes', 'tkinter', 'winreg']
for mod in required_modules:
    try:
        __import__(mod)
    except ImportError:
        messagebox.showerror("Autoloader Error", f"Missing module: {mod}")
        sys.exit()

# 🧠 Switch Definitions
switches = [
    {
        "name": "Dark Mode",
        "key": winreg.HKEY_CURRENT_USER,
        "path": r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        "value": "AppsUseLightTheme",
        "on": 0,
        "off": 1
    },
    {
        "name": "Transparency Effects",
        "key": winreg.HKEY_CURRENT_USER,
        "path": r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
        "value": "EnableTransparency",
        "on": 1,
        "off": 0
    },
    {
        "name": "Show Taskbar Search",
        "key": winreg.HKEY_CURRENT_USER,
        "path": r"Software\Microsoft\Windows\CurrentVersion\Search",
        "value": "SearchboxTaskbarMode",
        "on": 1,
        "off": 0
    },
    {
        "name": "Disable Telemetry",
        "key": winreg.HKEY_LOCAL_MACHINE,
        "path": r"Software\Policies\Microsoft\Windows\DataCollection",
        "value": "AllowTelemetry",
        "on": 0,
        "off": 1
    },
    {
        "name": "Disable Cortana",
        "key": winreg.HKEY_LOCAL_MACHINE,
        "path": r"Software\Policies\Microsoft\Windows\Windows Search",
        "value": "AllowCortana",
        "on": 0,
        "off": 1
    }
]

# 🧬 Registry Helpers
def get_registry_value(root, path, name):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except:
        return None

def set_registry_value(root, path, name, value):
    try:
        with winreg.CreateKeyEx(root, path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, name, 0, winreg.REG_DWORD, value)
            return True
    except Exception as e:
        messagebox.showerror("Mutation Error", f"Failed to toggle {name}: {e}")
        return False

# 🖼️ GUI Setup
root = tk.Tk()
root.title("🧬 DominionDeck Control Codex")
root.geometry("520x420")
root.configure(bg="#1e1e1e")

tk.Label(root, text="Persona: Privacy Guardian", fg="white", bg="#1e1e1e", font=("Segoe UI", 12)).pack(pady=10)

frame = tk.Frame(root, bg="#1e1e1e")
frame.pack(pady=10)

def toggle_switch(switch, var):
    new_value = switch["on"] if var.get() else switch["off"]
    success = set_registry_value(switch["key"], switch["path"], switch["value"], new_value)
    if success:
        print(f"🜂 [{switch['name']}] toggled to {new_value}")
        print(f"🜁 Codex Mutation → {switch['path']}\\{switch['value']} = {new_value}")
        print(f"🜃 Feedback: Persona mutation applied.\n")

for switch in switches:
    current = get_registry_value(switch["key"], switch["path"], switch["value"])
    var = tk.BooleanVar(value=(current == switch["on"]))
    row = tk.Frame(frame, bg="#1e1e1e")
    row.pack(fill="x", pady=5)
    tk.Label(row, text=switch["name"], fg="white", bg="#1e1e1e", width=30, anchor="w").pack(side="left")
    tk.Checkbutton(row, variable=var, command=lambda s=switch, v=var: toggle_switch(s, v), bg="#1e1e1e").pack(side="right")

root.mainloop()

