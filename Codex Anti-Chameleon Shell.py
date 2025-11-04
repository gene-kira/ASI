# === Autoloader Daemon ===
import subprocess, sys, importlib, threading, time, tkinter as tk
from tkinter import messagebox
import pyperclip
from datetime import datetime

REQUIRED_LIBS = {
    "confusables": "confusables",
    "regex": "regex",
    "rich": "rich",
    "pyperclip": "pyperclip",
    "unicodedata": None,
    "tkinter": None
}

def install_and_import(lib_name, pip_name=None):
    try:
        if pip_name:
            importlib.import_module(lib_name)
        else:
            __import__(lib_name)
    except ImportError:
        print(f"[!] {lib_name} missing. Installing...")
        if pip_name:
            subprocess.check_call([sys.executable, "-m", "pip", "install", pip_name])
        try:
            importlib.import_module(lib_name)
            print(f"[+] {lib_name} loaded.")
        except ImportError:
            print(f"[x] Failed to load {lib_name}.")

def autoload_libraries():
    for lib, pip_name in REQUIRED_LIBS.items():
        install_and_import(lib, pip_name)

autoload_libraries()

# === Spoof Detection Core ===
import regex as re
import unicodedata
from confusables import is_confusable

def detect_spoof(text):
    issues = []
    for i, char in enumerate(text):
        name = unicodedata.name(char, 'UNKNOWN')
        if is_confusable(char):
            issues.append((i, char, 'homoglyph', name))
        elif re.match(r'\p{Cf}', char):  # Format characters
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
def scan_text():
    input_text = text_box.get("1.0", tk.END)
    issues = detect_spoof(input_text)
    result_box.delete("1.0", tk.END)
    if issues:
        for i, char, issue_type, name in issues:
            result_box.insert(tk.END, f"[{issue_type.upper()}] '{char}' at index {i} — {name}\n")
        log_mutation(input_text, issues)
    else:
        result_box.insert(tk.END, "No spoofing detected.")

root = tk.Tk()
root.title("Codex Anti-Chameleon Shell")

text_box = tk.Text(root, height=10, width=60)
text_box.pack(pady=10)

scan_button = tk.Button(root, text="Scan for Spoofing", command=scan_text)
scan_button.pack()

result_box = tk.Text(root, height=10, width=60, bg="#111", fg="#0f0")
result_box.pack(pady=10)

# === Daemonized Clipboard Watcher ===
def clipboard_daemon():
    last_clip = ""
    while True:
        try:
            clip = pyperclip.paste()
            if clip != last_clip:
                last_clip = clip
                issues = detect_spoof(clip)
                if issues:
                    log_mutation(clip, issues)
                    messagebox.showwarning("Spoof Detected", f"Clipboard contains spoofed text!\n\n{clip}")
        except Exception as e:
            print(f"[Daemon Error] {e}")
        time.sleep(2)

threading.Thread(target=clipboard_daemon, daemon=True).start()

root.mainloop()

