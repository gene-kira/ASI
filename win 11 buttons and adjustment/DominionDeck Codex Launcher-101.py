# 🧬 DominionDeck Codex Launcher
# Author: killer666 + Copilot
# Description: Tactical GUI for Windows 11 control with elevation, presets, encryption, and mutation history

import sys, os, json, datetime, ctypes, tkinter as tk
from tkinter import ttk, messagebox
import winreg
from cryptography.fernet import Fernet

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

# 📦 Autoloader Check
required_modules = ['ctypes', 'tkinter', 'winreg', 'cryptography']
for mod in required_modules:
    try:
        __import__(mod)
    except ImportError:
        messagebox.showerror("Autoloader Error", f"Missing module: {mod}")
        sys.exit()

# 🧠 Registry Helpers
def get_registry_value(root, path, name):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, name)
            return value
    except:
        return None

def set_registry_value(root, path, name, value, value_type=winreg.REG_DWORD):
    try:
        with winreg.CreateKeyEx(root, path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, name, 0, value_type, value)
            return True
    except Exception as e:
        messagebox.showerror("Mutation Error", f"Failed to toggle {name}: {e}")
        return False

# 🧬 Mutation History
mutation_file = "mutation_log.json"

def log_mutation(switch, new_value):
    entry = {
        "timestamp": datetime.datetime.now().isoformat(),
        "name": switch["name"],
        "domain": switch["domain"],
        "path": switch["path"],
        "value": switch["value"],
        "new_value": new_value
    }
    if os.path.exists(mutation_file):
        with open(mutation_file, "r") as f:
            history = json.load(f)
    else:
        history = []
    history.append(entry)
    with open(mutation_file, "w") as f:
        json.dump(history, f, indent=2)
    print(f"🧬 Mutation logged: {entry['name']} → {new_value}")

def rollback_last():
    if not os.path.exists(mutation_file):
        messagebox.showinfo("Rollback", "No mutation history found.")
        return
    with open(mutation_file, "r") as f:
        history = json.load(f)
    if not history:
        messagebox.showinfo("Rollback", "Mutation log is empty.")
        return
    last = history.pop()
    value_type = winreg.REG_DWORD if isinstance(last["new_value"], int) else winreg.REG_SZ
    set_registry_value(
        winreg.HKEY_CURRENT_USER if last["domain"] != "Security" else winreg.HKEY_LOCAL_MACHINE,
        last["path"],
        last["value"],
        last["new_value"],
        value_type
    )
    with open(mutation_file, "w") as f:
        json.dump(history, f, indent=2)
    print(f"🜂 Rolled back: {last['name']} → {last['new_value']}")

# 🔐 Encrypted Profile Sync
key_file = "sync_key.key"
profile_file = "dominion_profile.enc"

def generate_key():
    key = Fernet.generate_key()
    with open(key_file, "wb") as f:
        f.write(key)

def load_key():
    if not os.path.exists(key_file):
        generate_key()
    with open(key_file, "rb") as f:
        return Fernet(f.read())

def export_encrypted_profile():
    fernet = load_key()
    profile = {}
    for switch in switches:
        current = get_registry_value(switch["key"], switch["path"], switch["value"])
        profile[switch["name"]] = current
    data = json.dumps(profile).encode()
    encrypted = fernet.encrypt(data)
    with open(profile_file, "wb") as f:
        f.write(encrypted)
    print("🧬 Encrypted profile exported.")

def import_encrypted_profile():
    fernet = load_key()
    try:
        with open(profile_file, "rb") as f:
            encrypted = f.read()
        decrypted = fernet.decrypt(encrypted)
        profile = json.loads(decrypted.decode())
        for switch in switches:
            if switch["name"] in profile:
                value = profile[switch["name"]]
                value_type = winreg.REG_DWORD if isinstance(value, int) else winreg.REG_SZ
                set_registry_value(switch["key"], switch["path"], switch["value"], value, value_type)
        print("🧬 Encrypted profile imported.")
    except Exception as e:
        messagebox.showerror("Import Error", f"Failed to import encrypted profile: {e}")

# 🧠 Role Presets
role_presets = {
    "Gamer": [
        "Disable Indexing", "Enable Legacy Volume Mixer", "Disable AutoPlay",
        "Disable Feedback Requests", "Disable Cortana", "Enable Transparency Effects"
    ],
    "Privacy Guardian": [
        "Disable Telemetry", "Disable Location Services", "Disable Advertising ID",
        "Disable SmartScreen", "Disable Defender Real-Time", "Disable Feedback Requests"
    ],
    "Minimalist": [
        "Show File Extensions", "Show Hidden Files", "Classic Context Menu",
        "Disable Recent Folders", "Disable Thumbnail Cache", "Disable Visual Effects"
    ]
}

def apply_role(role):
    for switch in switches:
        if switch["name"] in role_presets[role]:
            set_registry_value(switch["key"], switch["path"], switch["value"], switch["on"])
            log_mutation(switch, switch["on"])
        else:
            set_registry_value(switch["key"], switch["path"], switch["value"], switch["off"])
            log_mutation(switch, switch["off"])
    print(f"🧬 Role preset '{role}' applied.")

# 🧠 Switch Definitions (abbreviated for brevity—expand as needed)
switches = [
    {"domain": "UI & Shell", "name": "Dark Mode", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "value": "AppsUseLightTheme", "on": 0, "off": 1},
    {"domain": "Privacy", "name": "Disable Telemetry", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Policies\Microsoft\Windows\DataCollection", "value": "AllowTelemetry", "on": 0, "off": 1},
    {"domain": "Performance", "name": "Disable Indexing", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"SYSTEM\CurrentControlSet\Services\WSearch", "value": "Start", "on": 4, "off": 2},
    {"domain": "Explorer", "name": "Show File Extensions", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "value": "HideFileExt", "on": 0, "off": 1},
    {"domain": "Advanced", "name": "Classic Context Menu", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}", "value": "InprocServer32", "on": "", "off": None}
    # Add more switches here...
]

# 🖼️ GUI Setup
root = tk.Tk()
root.title("🧬 DominionDeck Codex Launcher")
root.geometry("900x600")
root.configure(bg="#1e1e1e")

style = ttk.Style()
style.theme_use("clam")
style.configure("TNotebook.Tab", background="#2e2e2e", foreground="white", padding=[10, 5])
style.configure("TCheckbutton", background="#1e1e1e", foreground="white")
style.configure("TLabel", background="#1e1e1e", foreground="white")

notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

# 🧩 Group switches by domain
domains = {}
for switch in switches:
    domain = switch["domain"]
    if domain not in domains:
        domains[domain] = []
    domains[domain].append(switch)

def toggle_switch(switch, var):
    new_value = switch["on"] if var.get() else switch["off"]
# 🔁 Toggle Logic
def toggle_switch(switch, var):
    new_value = switch["on"] if var.get() else switch["off"]
    value_type = winreg.REG_DWORD if isinstance(new_value, int) else winreg.REG_SZ
    success = set_registry_value(switch["key"], switch["path"], switch["value"], new_value, value_type)
    if success:
        log_mutation(switch, new_value)
        print(f"🜂 [{switch['name']}] toggled to {new_value}")
        print(f"🜁 Codex Mutation → {switch['path']}\\{switch['value']} = {new_value}")
        print(f"🜃 Feedback: Domain [{switch['domain']}] mutation applied.\n")

# 🧩 Build Tabs
for domain, items in domains.items():
    frame = tk.Frame(notebook, bg="#1e1e1e")
    notebook.add(frame, text=domain)

    for switch in items:
        current = get_registry_value(switch["key"], switch["path"], switch["value"])
        var = tk.BooleanVar(value=(current == switch["on"]))
        row = tk.Frame(frame, bg="#1e1e1e")
        row.pack(fill="x", pady=3, padx=10)
        label = ttk.Label(row, text=switch["name"], width=50)
        label.pack(side="left")
        check = ttk.Checkbutton(row, variable=var, command=lambda s=switch, v=var: toggle_switch(s, v))
        check.pack(side="right")

# 🧬 Control Panel Buttons
control_panel = tk.Frame(root, bg="#1e1e1e")
control_panel.pack(pady=5)

for role in role_presets:
    btn = tk.Button(control_panel, text=f"Apply {role}", command=lambda r=role: apply_role(r))
    btn.pack(side="left", padx=5)

tk.Button(control_panel, text="Export Profile", command=lambda: export_encrypted_profile()).pack(side="left", padx=5)
tk.Button(control_panel, text="Import Profile", command=lambda: import_encrypted_profile()).pack(side="left", padx=5)
tk.Button(control_panel, text="Rollback Last", command=rollback_last).pack(side="left", padx=5)

# 🧪 Launch GUI
root.mainloop()

