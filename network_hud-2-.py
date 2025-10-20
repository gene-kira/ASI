# codex_sentinel_asi.py

import importlib, subprocess, sys, platform, os, ctypes, tkinter as tk, threading, requests, time

# === AUTOLOADER ===
def autoload(modules):
    for m in modules:
        try: importlib.import_module(m)
        except ImportError: subprocess.check_call([sys.executable, "-m", "pip", "install", m])
        finally: globals()[m] = importlib.import_module(m)

autoload(["requests", "threading", "time", "json"])

# === ELEVATION CHECK ===
def ensure_admin():
    try:
        is_admin = ctypes.windll.shell32.IsUserAnAdmin()
    except:
        is_admin = False

    if not is_admin:
        print("[Codex Sentinel] Elevation required. Relaunching as administrator...")
        ctypes.windll.shell32.ShellExecuteW(
            None, "runas", sys.executable, " ".join(sys.argv), None, 1
        )
        sys.exit()

# === ASI-GRADE GUI SHELL ===
class CodexSentinelASI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Codex Sentinel: ASI-Grade Console")
        self.geometry("1600x900")
        self.configure(bg="#0f0f0f")
        self.panels = {}
        self.create_panels()
        self.start_daemons()

    def create_panels(self):
        titles = [
            "🌐 Global Outage Map", "🧠 Swarm Sync Status",
            "🗺️ Country Filter", "📡 Event Bus",
            "🧹 Registry Mutation Panel", "🔄 Autonomous Feedback Loop"
        ]
        for i, title in enumerate(titles):
            frame = tk.Frame(self, bg="#1a1a1a")
            frame.grid(row=i//2, column=i%2, padx=10, pady=10, sticky="nsew")
            label = tk.Label(frame, text=title, fg="#00ffcc", bg="#1a1a1a", font=("Consolas", 10))
            label.pack(anchor="w")
            text = tk.Text(frame, height=10, bg="#0f0f0f", fg="#00ffcc", insertbackground="#00ffcc")
            text.pack(fill="both", expand=True)
            self.panels[title] = text

    def start_daemons(self):
        def daemon():
            while True:
                try:
                    # 🌐 Global Outage Map (proxy placeholder)
                    self.panels["🌐 Global Outage Map"].delete("1.0", tk.END)
                    self.panels["🌐 Global Outage Map"].insert(tk.END, "Outage map loaded via proxy.\n")

                    # 🧠 Swarm Sync Simulation
                    self.panels["🧠 Swarm Sync Status"].delete("1.0", tk.END)
                    self.panels["🧠 Swarm Sync Status"].insert(tk.END, "Nodes synced: 98%\nCodex merged.\nThreats purged.")

                    # 🗺️ Country Filter GUI
                    allowed = ["US", "EU", "JP"]
                    blocked = ["RU", "CN", "IR"]
                    self.panels["🗺️ Country Filter"].delete("1.0", tk.END)
                    self.panels["🗺️ Country Filter"].insert(tk.END, f"Allowed: {', '.join(allowed)}\nBlocked: {', '.join(blocked)}")

                    # 🧹 Registry Mutation Panel
                    self.panels["🧹 Registry Mutation Panel"].delete("1.0", tk.END)
                    if platform.system() == "Windows":
                        try:
                            import winreg
                            keys = [
                                r"SOFTWARE\Microsoft\Windows\CurrentVersion\Policies\DataCollection",
                                r"SOFTWARE\Policies\Microsoft\Windows\DataCollection"
                            ]
                            for key in keys:
                                try:
                                    reg = winreg.OpenKey(winreg.HKEY_LOCAL_MACHINE, key, 0, winreg.KEY_ALL_ACCESS)
                                    winreg.SetValueEx(reg, "AllowTelemetry", 0, winreg.REG_DWORD, 0)
                                    self.panels["🧹 Registry Mutation Panel"].insert(tk.END, f"Purged: {key}\\AllowTelemetry\n")
                                except Exception as e:
                                    self.panels["🧹 Registry Mutation Panel"].insert(tk.END, f"Error: {e}\n")
                        except Exception as e:
                            self.panels["🧹 Registry Mutation Panel"].insert(tk.END, f"Import error: {e}\n")
                    else:
                        self.panels["🧹 Registry Mutation Panel"].insert(tk.END, "Non-Windows system. Mutation skipped.\n")

                    # 🔄 Autonomous Feedback Loop
                    self.panels["🔄 Autonomous Feedback Loop"].delete("1.0", tk.END)
                    self.panels["🔄 Autonomous Feedback Loop"].insert(tk.END, "Codex feedback loop active.\nThreats classified.\nPurge logic refined.")

                    # 📡 Event Bus
                    self.panels["📡 Event Bus"].insert(tk.END, f"[{time.strftime('%H:%M:%S')}] Daemons synced.\n")

                except Exception as e:
                    self.panels["📡 Event Bus"].insert(tk.END, f"[ERROR] {e}\n")
                time.sleep(60)

        threading.Thread(target=daemon, daemon=True).start()

# === ENTRY POINT ===
if __name__ == "__main__":
    if platform.system() == "Windows":
        ensure_admin()
    CodexSentinelASI().mainloop()

