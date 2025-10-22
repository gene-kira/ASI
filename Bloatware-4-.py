import subprocess
import sys
import tkinter as tk
from tkinter import ttk, messagebox
import winreg
import uuid

# 🧠 Friendly name mapping for UWP packages
friendly_names = {
    "Microsoft.XboxGamingOverlay": "Xbox Game Bar",
    "Microsoft.Clipchamp": "Clipchamp Video Editor",
    "Microsoft.SkypeApp": "Skype",
    "Microsoft.MicrosoftSolitaireCollection": "Solitaire Collection",
    "Microsoft.YourPhone": "Phone Link",
    "Microsoft.MSPaint": "Paint",
    "Microsoft.MixedReality.Portal": "Mixed Reality Portal",
    "Microsoft.WindowsCamera": "Camera",
    "Microsoft.WindowsMaps": "Maps",
    "Microsoft.WindowsAlarms": "Alarms & Clock",
    "Microsoft.WindowsCalculator": "Calculator",
    "Microsoft.WindowsSoundRecorder": "Sound Recorder"
}

# 🔮 Known Microsoft Bloatware Registry
known_bloatware = {
    "Candy Crush": {"origin": "Microsoft Store", "threat": "Medium"},
    "Xbox": {"origin": "System Component", "threat": "Low"},
    "Skype": {"origin": "Microsoft Store", "threat": "Low"},
    "OneNote": {"origin": "Bundled", "threat": "Low"},
    "News": {"origin": "Microsoft Store", "threat": "Medium"},
    "Phone Link": {"origin": "System Component", "threat": "Medium"},
    "3D Viewer": {"origin": "Optional Feature", "threat": "Low"},
    "Paint 3D": {"origin": "Optional Feature", "threat": "Low"},
    "Mixed Reality": {"origin": "Optional Feature", "threat": "Low"},
    "Solitaire": {"origin": "Microsoft Store", "threat": "Medium"},
    "Teams": {"origin": "Bundled", "threat": "Medium"},
    "Clipchamp": {"origin": "Microsoft Store", "threat": "Medium"},
    "Cortana": {"origin": "System Component", "threat": "Medium"}
}

def get_bloatware_confidence(name):
    score = 0
    if any(x in name.lower() for x in ["viewer", "portal", "link", "news", "clip", "solitaire", "cortana", "xbox", "candy"]):
        score += 40
    if "telemetry" in name.lower() or "tracker" in name.lower():
        score += 30
    return min(score, 100)

def scan_registry_apps():
    results = []
    uninstall_keys = [
        r"SOFTWARE\Microsoft\Windows\CurrentVersion\Uninstall",
        r"SOFTWARE\WOW6432Node\Microsoft\Windows\CurrentVersion\Uninstall"
    ]
    for root in [winreg.HKEY_LOCAL_MACHINE, winreg.HKEY_CURRENT_USER]:
        for key_path in uninstall_keys:
            try:
                with winreg.OpenKey(root, key_path) as key:
                    for i in range(winreg.QueryInfoKey(key)[0]):
                        try:
                            subkey_name = winreg.EnumKey(key, i)
                            with winreg.OpenKey(key, subkey_name) as subkey:
                                name = winreg.QueryValueEx(subkey, "DisplayName")[0]
                                match_type = "Heuristic"
                                origin = "Unknown"
                                threat = "Medium"
                                known = False
                                for k in known_bloatware:
                                    if k.lower() in name.lower():
                                        meta = known_bloatware[k]
                                        origin = meta["origin"]
                                        threat = meta["threat"]
                                        match_type = "Exact" if k.lower() == name.lower() else "Partial"
                                        known = True
                                        break
                                bci = 100 if known else get_bloatware_confidence(name)
                                if known or bci >= 40:
                                    results.append((name, origin, threat, bci, str(known), "Win32", match_type))
                        except Exception:
                            continue
            except Exception:
                continue
    return results

def scan_uwp_apps():
    results = []
    try:
        output = subprocess.check_output(["powershell", "-Command", "Get-AppxPackage | Select Name"], shell=True, text=True)
        lines = output.splitlines()
        for line in lines:
            name = line.strip()
            if not name or name.startswith("Name") or name.startswith("--"):
                continue
            friendly = friendly_names.get(name, name)
            match_type = "Heuristic"
            origin = "Unknown"
            threat = "Medium"
            known = False
            for k in known_bloatware:
                if k.lower() in friendly.lower():
                    meta = known_bloatware[k]
                    origin = meta["origin"]
                    threat = meta["threat"]
                    match_type = "Exact" if k.lower() == friendly.lower() else "Partial"
                    known = True
                    break
            bci = 100 if known else get_bloatware_confidence(friendly)
            if known or bci >= 40:
                results.append((friendly, origin, threat, bci, str(known), "UWP", match_type))
    except Exception as e:
        print(f"[!] UWP scan failed: {e}")
    return results

def purge_app(name, app_type):
    try:
        if app_type == "Win32":
            subprocess.run(["wmic", "product", "where", f"name='{name}'", "call", "uninstall"], shell=True)
        elif app_type == "UWP":
            subprocess.run(["powershell", "-Command", f"Get-AppxPackage -Name '{name}' | Remove-AppxPackage"], shell=True)
        messagebox.showinfo("Purged", f"{name} has been purged.")
    except Exception as e:
        messagebox.showerror("Error", f"Failed to purge {name}: {e}")

def launch_gui():
    root = tk.Tk()
    root.title("Windows Bloatware Scanner")
    root.geometry("1200x600")

    columns = ("Name", "Origin", "Threat", "BCI", "Known", "Type", "Match")
    tree = ttk.Treeview(root, columns=columns, show="headings")
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=150)
    tree.column("Name", width=250)
    tree.pack(fill=tk.BOTH, expand=True)

    toggle_states = {}

    results = scan_registry_apps() + scan_uwp_apps()
    if not results:
        messagebox.showinfo("Scan Complete", "No Microsoft-native bloatware detected.")
    else:
        for item in results:
            app_id = str(uuid.uuid4())
            tree.insert("", tk.END, iid=app_id, values=item)
            toggle_states[app_id] = tk.BooleanVar(value=False)

    # Toggle panel
    toggle_frame = tk.Frame(root)
    toggle_frame.pack(fill=tk.X)

    def refresh_toggles():
        for iid in tree.get_children():
            if iid not in toggle_states:
                continue
            cb = tk.Checkbutton(toggle_frame, text=tree.item(iid)["values"][0], variable=toggle_states[iid])
            cb.pack(anchor="w")

    refresh_toggles()

    def purge_selected():
        for iid in tree.get_children():
            if toggle_states.get(iid) and toggle_states[iid].get():
                item = tree.item(iid)["values"]
                name = item[0]
                app_type = item[5]
                purge_app(name, app_type)

    purge_btn = tk.Button(root, text="🔥 Purge Toggled Apps", command=purge_selected)
    purge_btn.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    try:
        launch_gui()
    except Exception as e:
        print(f"[CRITICAL] GUI failed to launch: {e}")
        input("Press Enter to exit...")

