# 🧬 DominionDeck Codex Launcher (Section 1)
import sys
import ctypes
import tkinter as tk
from tkinter import ttk, messagebox
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

# 📦 Autoloader Check
required_modules = ['ctypes', 'tkinter', 'winreg']
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

# 🧠 Switch Definitions (Grouped by Domain)
switches = [

    # 🧩 UI & Shell
    {"domain": "UI & Shell", "name": "Dark Mode", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "value": "AppsUseLightTheme", "on": 0, "off": 1},
    {"domain": "UI & Shell", "name": "Transparency Effects", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Themes\Personalize", "value": "EnableTransparency", "on": 1, "off": 0},
    {"domain": "UI & Shell", "name": "Taskbar Alignment (Center)", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "value": "TaskbarAl", "on": 1, "off": 0},
    {"domain": "UI & Shell", "name": "Snap Assist", "key": winreg.HKEY_CURRENT_USER, "path": r"Control Panel\Desktop", "value": "DockMoving", "on": 1, "off": 0},
    {"domain": "UI & Shell", "name": "Show File Extensions", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "value": "HideFileExt", "on": 0, "off": 1},
    {"domain": "UI & Shell", "name": "Show Hidden Files", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "value": "Hidden", "on": 1, "off": 2},
    {"domain": "UI & Shell", "name": "Classic Context Menu", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Classes\CLSID\{86ca1aa0-34aa-4e8b-a509-50c905bae2a2}", "value": "InprocServer32", "on": "", "off": None},

    # 🛡️ Privacy
    {"domain": "Privacy", "name": "Disable Telemetry", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Policies\Microsoft\Windows\DataCollection", "value": "AllowTelemetry", "on": 0, "off": 1},
    {"domain": "Privacy", "name": "Disable Advertising ID", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\AdvertisingInfo", "value": "Enabled", "on": 0, "off": 1},
    {"domain": "Privacy", "name": "Disable Location Services", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"SOFTWARE\Microsoft\Windows\CurrentVersion\CapabilityAccessManager\ConsentStore\location", "value": "Value", "on": "Deny", "off": "Allow"},
    {"domain": "Privacy", "name": "Disable Feedback Requests", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Microsoft\Windows\Feedback", "value": "FeedbackFrequency", "on": 0, "off": 1},

    # ⚡ Performance
    {"domain": "Performance", "name": "Disable Indexing", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"SYSTEM\CurrentControlSet\Services\WSearch", "value": "Start", "on": 4, "off": 2},
    {"domain": "Performance", "name": "Disable Background Apps", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\BackgroundAccessApplications", "value": "GlobalUserDisabled", "on": 1, "off": 0},
    {"domain": "Performance", "name": "Disable Visual Effects", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\VisualEffects", "value": "VisualFXSetting", "on": 2, "off": 1},

    # ♿ Accessibility
    {"domain": "Accessibility", "name": "Enable High Contrast", "key": winreg.HKEY_CURRENT_USER, "path": r"Control Panel\Accessibility\HighContrast", "value": "Flags", "on": 1, "off": 0},
    {"domain": "Accessibility", "name": "Enable Sticky Keys", "key": winreg.HKEY_CURRENT_USER, "path": r"Control Panel\Accessibility\StickyKeys", "value": "Flags", "on": 510, "off": 506},

    # 🌐 Networking
    {"domain": "Networking", "name": "Set Ethernet as Metered", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"SOFTWARE\Microsoft\Windows NT\CurrentVersion\NetworkList\DefaultMediaCost", "value": "Ethernet", "on": 2, "off": 1},
    {"domain": "Networking", "name": "Disable Proxy", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Internet Settings", "value": "ProxyEnable", "on": 0, "off": 1},

    # 🔐 Security
    {"domain": "Security", "name": "Disable SmartScreen", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer", "value": "SmartScreenEnabled", "on": "Off", "off": "Prompt"},
    {"domain": "Security", "name": "Disable Defender Real-Time", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Policies\Microsoft\Windows Defender\Real-Time Protection", "value": "DisableRealtimeMonitoring", "on": 1, "off": 0},

    # 📁 Explorer
    {"domain": "Explorer", "name": "Disable Recent Folders", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "value": "Start_TrackDocs", "on": 0, "off": 1},
    {"domain": "Explorer", "name": "Disable Thumbnail Cache", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\Advanced", "value": "DisableThumbnailCache", "on": 1, "off": 0},

    # 🔄 Updates
    {"domain": "Updates", "name": "Disable Auto Restart", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Policies\Microsoft\Windows\WindowsUpdate\AU", "value": "NoAutoRebootWithLoggedOnUsers", "on": 1, "off": 0},
    {"domain": "Updates", "name": "Defer Feature Updates", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Policies\Microsoft\Windows\WindowsUpdate\AU", "value": "DeferFeatureUpdates", "on": 1, "off": 0},

    # ⚙️ System Behavior
    {"domain": "System", "name": "Disable Fast Startup", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"SYSTEM\CurrentControlSet\Control\Session Manager\Power", "value": "HiberbootEnabled", "on": 0, "off": 1},
    {"domain": "System", "name": "Disable AutoPlay", "key": winreg.HKEY_CURRENT_USER, "path": r"Software\Microsoft\Windows\CurrentVersion\Explorer\AutoplayHandlers", "value": "DisableAutoplay", "on": 1, "off": 0},

    # 🧪 Advanced Flags
    {"domain": "Advanced", "name": "Enable Legacy Volume Mixer", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Microsoft\Windows\CurrentVersion\MMDevices\Audio\Render", "value": "LegacyMixer", "on": 1, "off": 0},
    {"domain": "Advanced", "name": "Enable Immersive Context Menu", "key": winreg.HKEY_LOCAL_MACHINE, "path": r"Software\Microsoft\Windows\CurrentVersion\FlightedFeatures", "value": "ImmersiveContextMenu", "on": 1, "off": 0}
]
# 🖼️ DominionDeck GUI Interface
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

# 🧠 Group switches by domain
domains = {}
for switch in switches:
    domain = switch["domain"]
    if domain not in domains:
        domains[domain] = []
    domains[domain].append(switch)

# 🔁 Toggle Logic
def toggle_switch(switch, var):
    new_value = switch["on"] if var.get() else switch["off"]
    value_type = winreg.REG_DWORD if isinstance(new_value, int) else winreg.REG_SZ
    success = set_registry_value(switch["key"], switch["path"], switch["value"], new_value, value_type)
    if success:
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

# 🧪 Launch GUI
root.mainloop()
