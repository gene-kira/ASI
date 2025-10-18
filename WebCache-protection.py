import os, sys, time, socket, threading, hashlib, pyperclip, psutil, tkinter as tk
from tkinter import ttk
from datetime import datetime

# 🧬 Daemon Core
class CodexSentinel:
    def __init__(self):
        self.stream, self.log, self.comparisons = [], [], []
        self.charge, self.nodes, self.folder = 100, [SwarmNode() for _ in range(3)], "WebCache"

    def rotor(self, data): return int(hashlib.sha256(data.encode()).hexdigest()[:4], 16) % 360
    def pulse(self, data): return data[::-1] if self.charge >= 20 else data
    def mutate(self, data):
        angle = self.rotor(data)
        mutated = self.pulse(data) if 85 <= angle <= 95 else data
        if mutated != data: self.charge -= 20; self.log.append(f"⚡ {data} → {mutated}")
        [n.sync(angle) for n in self.nodes if 85 <= angle <= 95]
        self.comparisons.append((datetime.now().strftime("%H:%M:%S"), data, mutated, angle))
        return mutated

    def protect(self):
        os.makedirs(self.folder, exist_ok=True)
        os.system(f'attrib +h +r "{self.folder}"')
        os.system(f'icacls "{self.folder}" /deny Everyone:(N)')
        for root, _, files in os.walk(self.folder):
            for f in files:
                try: os.chmod(os.path.join(root, f), 0o400)
                except: pass

    def scan_scripts(self):
        return [os.path.join(r, f) for r, _, fs in os.walk(self.folder) for f in fs if f.endswith((".js",".bat",".ps1",".py"))]

    def monitor_clipboard(self):
        last = ""
        while True:
            clip = pyperclip.paste().strip()
            if clip and clip != last: last = clip; self.stream.append(clip)
            time.sleep(2)

    def monitor_network(self):
        while True:
            try:
                for c in psutil.net_connections(kind='tcp'):
                    if c.status == 'ESTABLISHED':
                        self.stream.append(f"{c.laddr.ip}:{c.laddr.port} → {c.raddr.ip}:{c.raddr.port}")
            except: pass
            time.sleep(5)

    def listen_ports(self):
        s = socket.socket(); s.bind(("0.0.0.0", 0)); s.listen(100)
        while True:
            try:
                conn, _ = s.accept()
                threading.Thread(target=lambda: self.stream.append(conn.recv(1024).decode().strip()), daemon=True).start()
            except: pass

# 🧠 Swarm Node
class SwarmNode:
    def sync(self, angle): print(f"Node synced at {angle}° — pulse injected.")

# 🧙 GUI Overlay
def launch_gui(d):
    root = tk.Tk(); root.title("Codex Sentinel"); root.geometry("700x950"); root.configure(bg="#0a0f1c")
    status = tk.StringVar(value="Daemon initialized.")
    widgets = {
        "status": tk.Label(root, textvariable=status, font=("Consolas", 10), fg="orange", bg="#0a0f1c"),
        "torque": tk.Canvas(root, width=650, height=150, bg="black"),
        "bar": ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate"),
        "log": tk.Text(root, height=10, width=85, font=("Consolas", 9), bg="#111", fg="white"),
        "compare": tk.Text(root, height=10, width=85, font=("Consolas", 9), bg="#111", fg="lightgreen"),
        "timing": tk.Canvas(root, width=650, height=150, bg="#222"),
        "threat": tk.Text(root, height=5, width=85, font=("Consolas", 9), bg="#111", fg="red")
    }
    [tk.Label(root, text="Codex Sentinel", font=("Consolas", 18), fg="cyan", bg="#0a0f1c").pack(pady=10)]
    [w.pack(pady=5) for w in widgets.values()]

    def refresh():
        while True:
            d.charge = min(d.charge + 1, 100)
            d.protect()
            processed = [d.mutate(x) for x in d.stream]; d.stream.clear()
            status.set("⚙️ Stream processed."); widgets["bar"]["value"] = d.charge
            widgets["log"].delete("1.0", tk.END)
            [widgets["log"].insert(tk.END, l + "\n") for l in d.log[-10:]]
            widgets["torque"].delete("all")
            for i, data in enumerate(processed[-10:]):
                x, h = i * 60 + 30, 100 if "⚡" in d.log[-10:][i] else 40
                widgets["torque"].create_line(x, 120, x, 120 - h, fill="orange" if h == 100 else "cyan", width=4)
            widgets["compare"].delete("1.0", tk.END)
            for ts, raw, mut, angle in d.comparisons[-10:]:
                pulse = "⚡" if 85 <= angle <= 95 else "—"
                widgets["compare"].insert(tk.END, f"{pulse} {angle:3}° | Raw: {raw} → {mut}\n")
            widgets["timing"].delete("all")
            for i, (ts, _, _, angle) in enumerate(d.comparisons[-10:]):
                x = i * 60 + 30
                widgets["timing"].create_oval(x-5, 115, x+5, 125, fill="orange" if 85 <= angle <= 95 else "cyan")
                widgets["timing"].create_text(x, 100, text=ts, fill="white", font=("Consolas", 8))
            widgets["threat"].delete("1.0", tk.END)
            [widgets["threat"].insert(tk.END, f"⚠️ Script: {t}\n") for t in d.scan_scripts()]
            time.sleep(3)

    threading.Thread(target=refresh, daemon=True).start()
    root.mainloop()

# 🧨 Entry Point
if __name__ == "__main__":
    daemon = CodexSentinel()
    [threading.Thread(target=f, daemon=True).start() for f in [
        daemon.monitor_clipboard, daemon.monitor_network, daemon.listen_ports,
        lambda: launch_gui(daemon)
    ]]
    while True: daemon.charge = min(daemon.charge + 1, 100); time.sleep(10)

