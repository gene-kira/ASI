# ━━━━━━━━━━━━━━━━ PREFLIGHT ━━━━━━━━━━━━━━━━
import os, sys, subprocess, platform, socket

REQUIRED_LIBS = ['tkinter', 'psutil']
REQUIRED_FONT = "Orbitron"
REQUIRED_OS = ["Windows", "Linux", "Darwin"]

def ensure_libraries():
    for lib in REQUIRED_LIBS:
        try:
            __import__(lib)
        except ImportError:
            print(f"⚠️ Missing '{lib}'. Attempting install...")
            try:
                subprocess.check_call([sys.executable, "-m", "pip", "install", lib])
                print(f"✅ Installed '{lib}'.")
            except Exception as e:
                print(f"❌ Install failed for '{lib}': {e}")
                sys.exit(1)

def verify_environment():
    current_os = platform.system()
    if current_os not in REQUIRED_OS:
        print(f"❌ Unsupported OS: {current_os}")
        sys.exit(1)
    else:
        print(f"✅ OS verified: {current_os}")

def font_check():
    try:
        import tkinter as tk
        import tkinter.font as tkFont
        root = tk.Tk()
        fonts = tkFont.families()
        root.destroy()
        if REQUIRED_FONT not in fonts:
            print(f"⚠️ Font '{REQUIRED_FONT}' not found.")
        else:
            print(f"✅ Font '{REQUIRED_FONT}' available.")
    except Exception as e:
        print(f"⚠️ Font check failed: {e}")

def run_preflight():
    print("\n🧠 OVERMIND PREFLIGHT INITIATED\n")
    ensure_libraries()
    verify_environment()
    font_check()
    print("⚡ Integrity check complete. Preparing Overmind...\n")

run_preflight()

# ━━━━━━━━━━━━━━━━ SYSTEM HOOKS ━━━━━━━━━━━━━━━━
import psutil
import tkinter as tk
from tkinter import ttk

def fetch_persona_state():
    system = platform.system()
    hostname = socket.gethostname()
    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory().percent

    if cpu < 30 and ram < 50:
        mood = "Calm"
    elif cpu < 65:
        mood = "Alert"
    elif cpu < 90:
        mood = "Hostile"
    else:
        mood = "Transcendent"

    glyph = "🖥️" if system == "Windows" else "🧬"

    return {
        "name": hostname or "Overmind",
        "mood": mood,
        "glyph": glyph
    }

def fetch_threat_level():
    cpu = psutil.cpu_percent()
    disk = psutil.disk_usage('/').percent
    net = psutil.net_io_counters().packets_sent

    if cpu > 90 or disk > 90:
        return "Critical"
    elif cpu > 70 or net > 50000:
        return "Elevated"
    elif cpu > 40:
        return "Low"
    else:
        return "None"

def fetch_emotional_color(mood):
    mood_map = {
        "Calm": "#5DADE2",
        "Alert": "#F4D03F",
        "Hostile": "#E74C3C",
        "Transcendent": "#9B59B6"
    }
    return mood_map.get(mood, "#2C3E50")

# ━━━━━━━━━━━━━━━━ GUI CORE ━━━━━━━━━━━━━━━━
class OvermindGUI(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Overmind: Genesis Core")
        self.geometry("800x600")
        self.configure(bg="#1C1C1C")
        self.setup_styles()
        self.create_panels()
        self.refresh_data()

    def setup_styles(self):
        style = ttk.Style()
        style.theme_use('default')
        style.configure("Overmind.TLabelframe", background="#1C1C1C", foreground="white")
        style.configure("Overmind.TLabelframe.Label", foreground="cyan", font=(REQUIRED_FONT, 12))

    def create_panels(self):
        self.persona_frame = ttk.LabelFrame(self, text="Active Persona", style="Overmind.TLabelframe")
        self.persona_frame.pack(padx=10, pady=10, fill="x")
        self.persona_label = tk.Label(self.persona_frame, text="", font=(REQUIRED_FONT, 20), fg="white", bg="#1C1C1C")
        self.persona_label.pack()

        self.canvas_frame = ttk.LabelFrame(self, text="Neural Canvas", style="Overmind.TLabelframe")
        self.canvas_frame.pack(padx=10, pady=10, fill="both", expand=True)
        self.canvas = tk.Canvas(self.canvas_frame, bg="#2C3E50")
        self.canvas.pack(fill="both", expand=True)

        self.threat_frame = ttk.LabelFrame(self, text="Threat Assessment", style="Overmind.TLabelframe")
        self.threat_frame.pack(padx=10, pady=10, fill="x")
        self.threat_label = tk.Label(self.threat_frame, text="", font=(REQUIRED_FONT, 16), fg="white", bg="#1C1C1C")
        self.threat_label.pack()

    def refresh_data(self):
        persona = fetch_persona_state()
        threat = fetch_threat_level()
        mood_color = fetch_emotional_color(persona["mood"])

        self.persona_label.config(text=f"{persona['glyph']} {persona['name']} – {persona['mood']}")
        self.threat_label.config(text=f"Threat Level: {threat}")
        self.canvas.config(bg=mood_color)
        self.canvas.delete("all")
        self.after(2500, self.refresh_data)

# ━━━━━━━━━━━━━━━━ IGNITION ━━━━━━━━━━━━━━━━
if __name__ == "__main__":
    OvermindGUI().mainloop()

