import subprocess, sys, importlib, threading, time, unicodedata
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
import tkinter as tk

def detect_spoof(text):
    issues = []
    for i, char in enumerate(text):
        name = unicodedata.name(char, 'UNKNOWN')
        if is_confusable(char):
            issues.append((i, char, 'homoglyph', name))
        elif re.match(r'\p{Cf}', char):
            issues.append((i, char, 'invisible', name))
    return issues

def log_mutation(text, issues):
    if not issues: return
    with open("mutation_log.txt", "a", encoding="utf-8") as log:
        log.write(f"\n[{datetime.now()}] Spoof detected:\n")
        log.write(f"Text: {text}\n")
        for i, char, issue_type, name in issues:
            log.write(f" - [{issue_type.upper()}] '{char}' at {i}: {name}\n")

# === GUI Shell ===
class AntiChameleonGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Codex Anti-Chameleon HUD")
        self.text_box = tk.Text(self.root, height=6, width=60)
        self.text_box.pack(pady=5)
        self.scan_button = tk.Button(self.root, text="Manual Scan", command=self.scan_text)
        self.scan_button.pack()
        self.result_box = tk.Text(self.root, height=12, width=60, bg="#111", fg="#0f0")
        self.result_box.pack(pady=5)
        self.log_button = tk.Button(self.root, text="View Mutation Log", command=self.load_log)
        self.log_button.pack()

    def scan_text(self):
        input_text = self.text_box.get("1.0", tk.END)
        issues = detect_spoof(input_text)
        self.result_box.delete("1.0", tk.END)
        if issues:
            for i, char, issue_type, name in issues:
                self.result_box.insert(tk.END, f"[{issue_type.upper()}] '{char}' at index {i} — {name}\n")
            log_mutation(input_text, issues)
        else:
            self.result_box.insert(tk.END, "No spoofing detected.")

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
def daemon_loop(gui_callback=None):
    last_clip = ""
    while True:
        try:
            clip = pyperclip.paste()
            if clip != last_clip:
                last_clip = clip
                issues = detect_spoof(clip)
                if issues:
                    log_mutation(clip, issues)
                    if gui_callback:
                        gui_callback(clip, issues)
        except Exception as e:
            print(f"[Daemon Error] {e}")
        time.sleep(2)

# === Launch Everything ===
def launch():
    gui = AntiChameleonGUI()
    threading.Thread(target=daemon_loop, daemon=True).start()
    gui.run()

if __name__ == "__main__":
    launch()

