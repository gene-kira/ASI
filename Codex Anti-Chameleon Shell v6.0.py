import subprocess, sys, importlib, threading, time, unicodedata, tkinter as tk
from datetime import datetime

# === Autoloader ===
REQUIRED_LIBS = {
    "confusables": "confusables",
    "regex": "regex",
    "pyperclip": "pyperclip",
    "tkinter": None,
    "unicodedata": None
}

def install_and_import(lib_name, pip_name=None):
    try:
        if pip_name:
            importlib.import_module(lib_name)
        else:
            __import__(lib_name)
    except ImportError:
        if pip_name:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        importlib.import_module(lib_name)

def autoload_libraries():
    for lib, pip_name in REQUIRED_LIBS.items():
        install_and_import(lib, pip_name)

autoload_libraries()

# === Spoof Detection Core ===
import regex as re
from confusables import is_confusable
import pyperclip

def detect_spoof(text):
    issues = []
    for i, char in enumerate(text):
        name = unicodedata.name(char, 'UNKNOWN')
        if is_confusable(char):
            issues.append((i, char, 'homoglyph', name))
        elif re.match(r'\p{Cf}', char):
            issues.append((i, char, 'invisible', name))
    return issues

def sanitize_text(text, issues):
    clean = list(text)
    for i, char, issue_type, _ in reversed(issues):
        if issue_type == 'invisible':
            del clean[i]
        elif issue_type == 'homoglyph':
            clean[i] = '?'  # Replace with placeholder or normalized glyph
    return ''.join(clean)

def log_mutation(text, issues, origin="clipboard"):
    if not issues: return
    with open("mutation_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.now()}] Spoof detected from {origin}:\n")
        log.write(f"Text: {text}\n")
        for i, char, issue_type, name in issues:
            log.write(f" - [{issue_type.upper()}] '{char}' at {i}: {name}\n")

# === Country Filter (stub logic) ===
ALLOWED_COUNTRIES = {"US", "CA", "UK"}  # Example whitelist

def is_country_allowed(country_code):
    return country_code in ALLOWED_COUNTRIES

def get_origin_country(text):
    # Placeholder: real implementation would use metadata or external API
    return "US"

# === Purge Shell Logic ===
def trigger_purge():
    print("[PURGE] Diagnostic lockdown triggered.")
    # Placeholder: real implementation would disable telemetry tasks, services, and feedback hub
    with open("mutation_log.txt", "a", encoding="utf-8") as log:
        log.write(f"[{datetime.now()}] Codex Purge Shell activated.\n")

# === GUI HUD with Animated Overlay ===
class AntiChameleonGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Codex Anti-Chameleon HUD")
        self.canvas = tk.Canvas(self.root, width=600, height=200, bg="black")
        self.canvas.pack()
        self.text_box = tk.Text(self.root, height=6, width=60)
        self.text_box.pack(pady=5)
        self.scan_button = tk.Button(self.root, text="Manual Scan", command=self.scan_text)
        self.scan_button.pack()
        self.result_box = tk.Text(self.root, height=12, width=60, bg="#111", fg="#0f0")
        self.result_box.pack(pady=5)
        self.log_button = tk.Button(self.root, text="View Mutation Log", command=self.load_log)
        self.log_button.pack()

    def draw_overlay(self, issues):
        self.canvas.delete("all")
        for i, char, issue_type, name in issues:
            x = 20 + (i * 10)
            color = "red" if issue_type == "homoglyph" else "cyan"
            self.canvas.create_text(x, 100, text=char, fill=color, font=("Courier", 14, "bold"))
            self.canvas.create_oval(x-5, 90, x+5, 110, outline=color)

    def scan_text(self):
        input_text = self.text_box.get("1.0", tk.END)
        issues = detect_spoof(input_text)
        self.result_box.delete("1.0", tk.END)
        if issues:
            for i, char, issue_type, name in issues:
                self.result_box.insert(tk.END, f"[{issue_type.upper()}] '{char}' at index {i} — {name}\n")
            self.draw_overlay(issues)
            log_mutation(input_text, issues, origin="manual")
            trigger_purge()
        else:
            self.result_box.insert(tk.END, "No spoofing detected.")
            self.canvas.delete("all")

    def load_log(self):
        try:
            with open("mutation_log.txt", "r", encoding="utf-8") as f:
                self.result_box.delete("1.0", tk.END)
                self.result_box.insert(tk.END, f.read())
        except FileNotFoundError:
            self.result_box.insert(tk.END, "No mutation log found.")

    def run(self):
        self.root.mainloop()

# === Daemon Loop ===
def daemon_loop():
    last_clip = ""
    while True:
        try:
            clip = pyperclip.paste()
            if clip != last_clip:
                last_clip = clip
                country = get_origin_country(clip)
                if not is_country_allowed(country):
                    print(f"[BLOCKED] Clipboard text from disallowed country: {country}")
                    continue
                issues = detect_spoof(clip)
                if issues:
                    log_mutation(clip, issues)
                    trigger_purge()
                    clean = sanitize_text(clip, issues)
                    pyperclip.copy(clean)
                    print(f"[!] Spoof detected and cleaned at {datetime.now()}")
        except Exception as e:
            print(f"[Daemon Error] {type(e).__name__}: {e}")
        time.sleep(2)

# === Launch Everything ===
def launch():
    gui = AntiChameleonGUI()
    threading.Thread(target=daemon_loop, daemon=True).start()
    gui.run()

if __name__ == "__main__":
    launch()

