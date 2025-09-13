import sys, os, json, datetime, ctypes, tkinter as tk
from tkinter import ttk, messagebox
import winreg, threading, time, random
from functools import partial
from cryptography.fernet import Fernet

def ensure_elevation():
    if not ctypes.windll.shell32.IsUserAnAdmin():
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1)
        sys.exit()

ensure_elevation()

def get_registry_value(root, path, name):
    try:
        with winreg.OpenKey(root, path, 0, winreg.KEY_READ) as key:
            return winreg.QueryValueEx(key, name)[0]
    except: return None

def set_registry_value(root, path, name, value, value_type=winreg.REG_DWORD):
    try:
        with winreg.CreateKeyEx(root, path, 0, winreg.KEY_WRITE) as key:
            winreg.SetValueEx(key, name, 0, value_type, value)
            return True
    except: return False

mutation_file = "mutation_log.json"
def log_mutation(switch, new_value):
    entry = { "timestamp": datetime.datetime.now().isoformat(), **switch, "new_value": new_value }
    history = []
    if os.path.exists(mutation_file):
        with open(mutation_file, "r") as f: history = json.load(f)
    history.append(entry)
    with open(mutation_file, "w") as f: json.dump(history, f, indent=2)

def rollback_last():
    if not os.path.exists(mutation_file): return
    with open(mutation_file, "r") as f: history = json.load(f)
    if not history: return
    last = history.pop()
    vt = winreg.REG_DWORD if isinstance(last["new_value"], int) else winreg.REG_SZ
    set_registry_value(winreg.HKEY_CURRENT_USER if last["domain"] != "Security" else winreg.HKEY_LOCAL_MACHINE,
                       last["path"], last["value"], last["new_value"], vt)
    with open(mutation_file, "w") as f: json.dump(history, f, indent=2)

key_file, profile_file = "sync_key.key", "dominion_profile.enc"
def load_key():
    if not os.path.exists(key_file):
        with open(key_file, "wb") as f: f.write(Fernet.generate_key())
    with open(key_file, "rb") as f: return Fernet(f.read())

def export_encrypted_profile():
    f = load_key()
    profile = {s["name"]: get_registry_value(s["key"], s["path"], s["value"]) for s in switches}
    with open(profile_file, "wb") as out: out.write(f.encrypt(json.dumps(profile).encode()))

def import_encrypted_profile():
    f = load_key()
    try:
        with open(profile_file, "rb") as inp:
            profile = json.loads(f.decrypt(inp.read()).decode())
        for s in switches:
            if s["name"] in profile:
                vt = winreg.REG_DWORD if isinstance(profile[s["name"]], int) else winreg.REG_SZ
                set_registry_value(s["key"], s["path"], s["value"], profile[s["name"]], vt)
    except: pass

role_presets = {
    "Gamer": ["Disable Indexing", "Enable Legacy Volume Mixer"],
    "Privacy Guardian": ["Disable Telemetry", "Disable Advertising ID"],
    "Minimalist": ["Show File Extensions", "Classic Context Menu"]
}

def apply_role(role):
    for s in switches:
        val = s["on"] if s["name"] in role_presets[role] else s["off"]
        set_registry_value(s["key"], s["path"], s["value"], val)
        log_mutation(s, val)

switches = [
    {"domain": "UI & Shell", "name": "Dark Mode", "key": winreg.HKEY_CURRENT_USER,
     "path": r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize",
     "value": "AppsUseLightTheme", "on": 0, "off": 1},
    {"domain": "Privacy", "name": "Disable Telemetry", "key": winreg.HKEY_LOCAL_MACHINE,
     "path": r"Software\Policies\Microsoft\Windows\DataCollection",
     "value": "AllowTelemetry", "on": 0, "off": 1},
    {"domain": "Explorer", "name": "Show File Extensions", "key": winreg.HKEY_CURRENT_USER,
     "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced",
     "value": "HideFileExt", "on": 0, "off": 1},
    {"domain": "Advanced", "name": "Classic Context Menu", "key": winreg.HKEY_CURRENT_USER,
     "path": r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}",
     "value": "InprocServer32", "on": "", "off": None}
]

root = tk.Tk()
root.title("🧬 DominionDeck Codex Launcher")
root.geometry("900x600")
root.configure(bg="#1e1e1e")

style = ttk.Style()
try: style.theme_use("clam")
except: style.theme_use("default")
style.configure("TNotebook.Tab", background="#2e2e2e", foreground="white", padding=[10, 5])
style.configure("TCheckbutton", background="#1e1e1e", foreground="white")
style.configure("TLabel", background="#1e1e1e", foreground="white")
notebook = ttk.Notebook(root)
notebook.pack(expand=True, fill="both", padx=10, pady=10)

domains = {}
for s in switches:
    domains.setdefault(s["domain"], []).append(s)

def toggle_switch(switch, var):
    new_value = switch["on"] if var.get() else switch["off"]
    vt = winreg.REG_DWORD if isinstance(new_value, int) else winreg.REG_SZ
    if set_registry_value(switch["key"], switch["path"], switch["value"], new_value, vt):
        log_mutation(switch, new_value)

for domain, items in domains.items():
    frame = tk.Frame(notebook, bg="#1e1e1e")
    notebook.add(frame, text=domain)
    for s in items:
        current = get_registry_value(s["key"], s["path"], s["value"])
        var = tk.BooleanVar(value=(current == s["on"]))
        row = tk.Frame(frame, bg="#1e1e1e")
        row.pack(fill="x", pady=3, padx=10)
        ttk.Label(row, text=s["name"], width=50).pack(side="left")
        ttk.Checkbutton(row, variable=var, command=partial(toggle_switch, s, var)).pack(side="right")

control_panel = tk.Frame(root, bg="#1e1e1e")
control_panel.pack(pady=5)

for role in role_presets:
    tk.Button(control_panel, text=f"Apply {role}", command=partial(apply_role, role)).pack(side="left", padx=5)

tk.Button(control_panel, text="Export Profile", command=export_encrypted_profile).pack(side="left", padx=5)
tk.Button(control_panel, text="Import Profile", command=import_encrypted_profile).pack(side="left", padx=5)
tk.Button(control_panel, text="Rollback Last", command=rollback_last).pack(side="left", padx=5)

def open_console():
    console = tk.Toplevel(root)
    console.title("🧬 Mutation Console")
    console.configure(bg="#1e1e1e")
    entry = tk.Entry(console, width=50)
    entry.pack(pady=10)

    def execute_command():
        cmd = entry.get().strip().lower()
        if cmd.startswith("mutate "):
            role = cmd.split(" ")[1].title()
            if role in role_presets: apply_role(role)
        elif cmd == "rollback all":
            if os.path.exists(mutation_file):
                with open(mutation_file, "r") as f: history = json.load(f)
                for entry in reversed(history):
                    vt = winreg.REG_DWORD if isinstance(entry["new_value"], int) else winreg.REG_SZ
                    set_registry_value(winreg.HKEY_CURRENT_USER if entry["domain"] != "Security" else winreg.HKEY_LOCAL_MACHINE,
                                       entry["path"], entry["value"], entry["new_value"], vt)
                open(mutation_file, "w").write("[]")
        elif cmd == "unlock vault": unlock_vault()

    tk.Button(console, text="Execute", command=execute_command).pack()

tk.Button(control_panel, text="Open Mutation Console", command=open_console).pack(side="left", padx=5)

glyph_sequence = []
glyph_unlock = ["up", "up", "down", "down", "left", "right", "left", "right", "b", "a"]

def glyph_input(event):
    glyph_sequence.append(event.keysym.lower())
    if glyph_sequence[-len(glyph_unlock):] == glyph_unlock:
        hidden_panel.pack(pady=10)

root.bind("<Key>", glyph_input)

hidden_panel = tk.Frame(root, bg="#2e2e2e")
tk.Label(hidden_panel, text="🧬 Hidden Codex Tools", fg="white", bg="#2e2e2e").pack()
tk.Button(hidden_panel, text="Force Registry Refresh", command=lambda: os.system("taskkill /f /im explorer.exe && start explorer")).pack(pady=5)
tk.Button(hidden_panel, text="Clear Mutation History", command=lambda: open(mutation_file, "w").write("[]")).pack(pady=5)
hidden_panel.pack_forget()

def watch_registry():
    while True:
        suspicious = get_registry_value(winreg.HKEY_LOCAL_MACHINE, r"Software\Microsoft\Windows\CurrentVersion\Policies\System", "EnableLUA")
        if suspicious == 0: print("🜃 ALERT: UAC disabled externally.")
        time.sleep(30)

root.after(1000, lambda: threading.Thread(target=watch_registry, daemon=True).start())

def safe_mainloop():
    try: root.mainloop()
    except Exception as e:
        import traceback
        traceback.print_exc()
        messagebox.showerror("Crash", f"GUI failed to load:\n{e}")

safe_mainloop()

