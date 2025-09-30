import os, threading, time, psutil, json
import tkinter as tk
from tkinter import scrolledtext
from flask import Flask, request, jsonify

# 🧿 Suspicious Patterns
PATTERNS = {
    b"gethostbyname": ("🌐", "Talks to the internet"),
    b"CreateProcess": ("⚙️", "Tries to run something"),
    b"tracking.js": ("📡", "Tracking script"),
    b"google-analytics": ("📊", "Google tracking"),
    b"XMLHttpRequest": ("🔗", "Fingerprinting trick"),
    b"canvas.toDataURL": ("🖼️", "Tries to read your screen"),
    b"WebSocket": ("📡", "Live connection to somewhere")
}

CRITICAL = {b"gethostbyname", b"CreateProcess", b"tracking.js", b"google-analytics"}

# ✅ Create extension folder next to script
def setup_extension():
    try:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        ext_dir = os.path.join(base_dir, "MagicBoxExtension")
        os.makedirs(ext_dir, exist_ok=True)

        manifest = {
            "manifest_version": 3,
            "name": "MagicBox Auto Scanner",
            "version": "1.0",
            "permissions": ["scripting", "tabs"],
            "host_permissions": ["<all_urls>"],
            "background": { "service_worker": "background.js" }
        }

        with open(os.path.join(ext_dir, "manifest.json"), "w") as f:
            json.dump(manifest, f, indent=2)

        background_js = """
chrome.tabs.onUpdated.addListener((tabId, changeInfo, tab) => {
  if (changeInfo.status === "complete" && tab.url.startsWith("http")) {
    chrome.scripting.executeScript({
      target: { tabId: tabId },
      func: () => {
        fetch("http://localhost:5000/scan", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({
            html: document.documentElement.outerHTML,
            url: window.location.href
          })
        });
      }
    });
  }
});
"""
        with open(os.path.join(ext_dir, "background.js"), "w") as f:
            f.write(background_js.strip())

        return ext_dir
    except Exception as e:
        return f"❌ Failed to create extension folder: {e}"

# 🧠 Task Manager Watcher
BROWSERS = ["chrome.exe", "firefox.exe", "msedge.exe", "brave.exe"]
seen_pids = set()

def browser_watcher(gui_callback):
    while True:
        for proc in psutil.process_iter(['pid', 'name']):
            name = proc.info['name']
            pid = proc.info['pid']
            if name in BROWSERS and pid not in seen_pids:
                seen_pids.add(pid)
                gui_callback(f"🧿 Browser opened: {name} (PID {pid})\n", "yellow", "Browser Launch")
        time.sleep(5)

# 🧰 Analyzer with Smarter Verdict
def analyze_bytes(content, origin="Unknown"):
    log = [f"🔍 Checking: {origin}\n"]
    severity = 0
    critical_hits = 0

    for p, (glyph, msg) in PATTERNS.items():
        if p in content:
            log.append(f"{glyph} {msg}\n")
            severity += 1
            if p in CRITICAL:
                critical_hits += 1

    if critical_hits == 0 and severity <= 1:
        verdict = "🟢 Legit"
        status = "green"
    elif critical_hits <= 1 and severity <= 3:
        verdict = "🟡 Caution"
        status = "yellow"
    else:
        verdict = "🔴 Suspicious"
        status = "red"

    log.append(f"\n🔎 Verdict: {verdict} ({severity} detections, {critical_hits} critical)\n✅ Done.\n")
    return "".join(log), status, verdict

# 🌐 Flask Server
flask_app = Flask(__name__)
gui_callback = None

@flask_app.route("/scan", methods=["POST"])
def scan_webpage():
    data = request.get_json()
    html = data.get("html", "").encode()
    url = data.get("url", "Unknown site")
    log, status, verdict = analyze_bytes(html, origin=url)
    if gui_callback: gui_callback(log, status, verdict)
    return jsonify({"status": "ok"})

def start_flask(): flask_app.run(port=5000, debug=False)

# 🎨 GUI
class MagicBoxApp:
    def __init__(self, root):
        global gui_callback
        gui_callback = self.update_gui
        root.title("🧿 MagicBox - Website Legitimacy Scanner")
        root.configure(bg="#222")

        self.status = tk.Label(root, text="Status: 🟢 Legit (0 detections)", bg="#0f0", fg="#000", font=("Arial", 14), width=50)
        self.status.pack(pady=10)

        self.log = scrolledtext.ScrolledText(root, bg="#000", fg="#0f0", font=("Courier", 12), width=80, height=25)
        self.log.pack(padx=10, pady=10)

        threading.Thread(target=start_flask, daemon=True).start()
        threading.Thread(target=browser_watcher, args=(self.update_gui,), daemon=True).start()

        ext_path = setup_extension()
        if "❌" in ext_path:
            self.log.insert(tk.END, f"\n{ext_path}\n")
        else:
            self.log.insert(tk.END, f"\n🧩 Extension folder created at:\n{ext_path}\n")
            self.log.insert(tk.END, "📦 Open Chrome → Extensions → Load unpacked → Select this folder\n")

    def update_gui(self, log, status, verdict):
        self.log.insert(tk.END, f"\n{log}\n"); self.log.see(tk.END)
        color = {"green": "#0f0", "yellow": "#ff0", "red": "#f00"}[status]
        self.status.config(text=f"Status: {verdict}", bg=color)

# 🚀 Launch
if __name__ == "__main__":
    root = tk.Tk()
    MagicBoxApp(root)
    root.mainloop()
