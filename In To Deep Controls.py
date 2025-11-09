import tkinter as tk
from tkinter import ttk, messagebox
import subprocess, sys, os

# 📝 Optional startup logging
try:
    with open("codex_purge_log.txt", "a") as log:
        log.write(f"Started with args: {sys.argv}\n")
except Exception:
    pass

# 🔧 Autoloader for required libraries
def autoload_libraries():
    required_libs = ["psutil", "win32com.client", "wmi"]
    for lib in required_libs:
        try:
            __import__(lib)
        except ImportError:
            subprocess.call([sys.executable, "-m", "pip", "install", lib])

# 🔐 Elevation check and relaunch
def is_admin():
    try:
        return os.getuid() == 0
    except AttributeError:
        import ctypes
        return ctypes.windll.shell32.IsUserAnAdmin()

def relaunch_as_admin():
    if not is_admin():
        import ctypes
        script = os.path.abspath(sys.argv[0])
        params = " ".join([f'"{arg}"' for arg in sys.argv[1:]])
        ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, f'"{script}" {params}', None, 1)
        sys.exit()

# 🧠 Group Policy Enforcement
def apply_group_policy():
    try:
        import winreg
        key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
        with winreg.CreateKeyEx(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_SET_VALUE) as key:
            winreg.SetValueEx(key, "AllowTelemetry", 0, winreg.REG_DWORD, 1)  # 1 = Basic
        messagebox.showinfo("Success", "Diagnostic level set to Basic via Group Policy.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to apply Group Policy: {e}")

# 🛑 Telemetry Service Suppression
def suppress_services():
    services = ["DiagTrack", "dmwappushsvc"]
    for svc in services:
        cmd = f'powershell -Command "Stop-Service -Name {svc} -Force; Set-Service -Name {svc} -StartupType Disabled"'
        subprocess.call(cmd, shell=True)
    messagebox.showinfo("Success", "Telemetry services suppressed.")

# 🗓️ Kill Scheduled Telemetry Tasks
def kill_telemetry_tasks():
    tasks = [
        r"ProgramDataUpdater",
        r"Proxy",
        r"Consolidator",
        r"UsbCeip",
        r"Microsoft-Windows-DiskDiagnosticDataCollector"
    ]
    for task in tasks:
        cmd = f'powershell -Command "Disable-ScheduledTask -TaskName \\"{task}\\" -Confirm:$false"'
        subprocess.call(cmd, shell=True)
    messagebox.showinfo("Success", "Telemetry tasks disabled.")

# 🧬 Swarm Sync Simulation
def simulate_swarm_sync():
    messagebox.showinfo("Action", "Swarm sync simulated.")

# 🧠 Threat Matrix Scan
def scan_threat_matrix():
    messagebox.showinfo("Action", "Threat matrix scanned.")

# 📊 Diagnostic Level Viewer
def show_diagnostic_level():
    try:
        import winreg
        key_path = r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
        with winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key_path, 0, winreg.KEY_READ) as key:
            value, _ = winreg.QueryValueEx(key, "AllowTelemetry")
            level = {0: "Security", 1: "Basic", 2: "Enhanced", 3: "Full"}.get(value, "Unknown")
            messagebox.showinfo("Diagnostic Level", f"Current level: {level}")
    except Exception:
        messagebox.showwarning("Diagnostic Level", "Unable to read diagnostic level.")

# 📜 Live Log Viewer
def view_logs():
    log_window = tk.Toplevel()
    log_window.title("Live Logs")
    log_text = tk.Text(log_window, wrap="word", height=20, width=80)
    log_text.insert("end", ">> Codex Purge Shell initialized...\n>> Awaiting purge triggers...\n")
    log_text.pack()

# 🖼️ GUI Layout
def build_gui():
    root = tk.Tk()
    root.title("Codex Purge Shell")
    root.geometry("800x600")

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill="both")

    # Panels
    panels = {
        "System Control": [
            ("Apply Group Policy", apply_group_policy),
            ("Kill Telemetry Tasks", kill_telemetry_tasks),
            ("Suppress Services", suppress_services)
        ],
        "Swarm Sync": [
            ("Simulate Node Sync", simulate_swarm_sync)
        ],
        "Threat Matrix": [
            ("Scan for Resurrection Glyphs", scan_threat_matrix)
        ],
        "Diagnostics": [
            ("Show Diagnostic Level", show_diagnostic_level)
        ],
        "Logs": [
            ("View Live Logs", view_logs)
        ]
    }

    for panel_name, buttons in panels.items():
        frame = ttk.Frame(notebook)
        notebook.add(frame, text=panel_name)
        for label, command in buttons:
            btn = ttk.Button(frame, text=label, command=command)
            btn.pack(pady=10, padx=10, anchor="w")

    root.mainloop()

# 🚀 Launch
if __name__ == "__main__":
    autoload_libraries()
    relaunch_as_admin()
    build_gui()

