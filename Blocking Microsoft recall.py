import tkinter as tk
from tkinter import messagebox, scrolledtext
import winreg
import subprocess
import os
import shutil

# 🧪 Autoloader: Confirm required modules
def ensure_libs():
    print("[*] Ensuring required libraries...")
    # All used modules are built-in for standard Python installs
    for lib in ["tkinter", "winreg", "os", "shutil", "subprocess"]:
        try:
            __import__(lib)
            print(f"[✓] {lib} loaded.")
        except ImportError:
            print(f"[!] {lib} missing. Install manually if needed.")

ensure_libs()

# 🧬 Recall Registry Toggle
def set_recall(enabled):
    try:
        key = winreg.CreateKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Recall")
        winreg.SetValueEx(key, "DisableSnapshots", 0, winreg.REG_DWORD, 0 if enabled else 1)
        winreg.CloseKey(key)
        status = "enabled" if enabled else "disabled"
        messagebox.showinfo("Recall Toggle", f"Recall has been {status}.")
        update_status()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# 🧹 Purge Snapshots
def purge_snapshots():
    path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Recall\Snapshots")
    try:
        shutil.rmtree(path, ignore_errors=True)
        messagebox.showinfo("Recall Toggle", "Snapshots deleted.")
        update_status()
    except Exception as e:
        messagebox.showerror("Error", str(e))

# 🔧 Service Toggle
def toggle_service(enable):
    subprocess.run(["sc", "config", "RecallService", "start=", "auto" if enable else "disabled"], shell=True)
    subprocess.run(["sc", "start" if enable else "stop", "RecallService"], shell=True)

# 🧿 Show Recall Status
def update_status():
    status_text.delete(1.0, tk.END)
    try:
        key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\Recall")
        value, _ = winreg.QueryValueEx(key, "DisableSnapshots")
        winreg.CloseKey(key)
        recall_status = "OFF" if value == 1 else "ON"
    except:
        recall_status = "UNKNOWN"

    snapshot_path = os.path.expandvars(r"%LOCALAPPDATA%\Microsoft\Windows\Recall\Snapshots")
    files = []
    if os.path.exists(snapshot_path):
        for root, dirs, filenames in os.walk(snapshot_path):
            for f in filenames:
                files.append(os.path.join(root, f))

    status_text.insert(tk.END, f"Recall Status: {recall_status}\n")
    status_text.insert(tk.END, f"Snapshot Count: {len(files)}\n\n")
    for f in files[:50]:
        status_text.insert(tk.END, f"{f}\n")
    if len(files) > 50:
        status_text.insert(tk.END, f"...and {len(files)-50} more\n")

# 🧠 GUI Setup
root = tk.Tk()
root.title("Recall Mutation Shell")
root.geometry("600x500")

tk.Label(root, text="Microsoft Recall Control Panel", font=("Arial", 16)).pack(pady=10)

tk.Button(root, text="Enable Recall", command=lambda: [set_recall(True), toggle_service(True)], bg="lightgreen").pack(pady=5)
tk.Button(root, text="Disable Recall", command=lambda: [set_recall(False), toggle_service(False), purge_snapshots()], bg="salmon").pack(pady=5)
tk.Button(root, text="Refresh Status", command=update_status, bg="lightblue").pack(pady=5)

status_text = scrolledtext.ScrolledText(root, wrap=tk.WORD, width=70, height=20)
status_text.pack(pady=10)

update_status()
root.mainloop()
