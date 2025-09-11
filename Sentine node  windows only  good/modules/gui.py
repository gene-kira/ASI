# gui.py
import tkinter as tk

class TacticalGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SentinelNode Interface")
        self.root.geometry("800x480")
        self.root.configure(bg="#0f1115")
        self._build_layout()

    def _build_layout(self):
        header = tk.Label(self.root, text="SENTINELNODE ACTIVE", font=("Consolas", 14, "bold"),
                          fg="#00ff88", bg="#0f1115", pady=4)
        header.pack(fill=tk.X)

        self.threat_log = self._frame("Threat Grid", "#ff4444", 10, 40, 380, 120)
        self.persona_display = self._listbox("Persona Overlay", "#00ffff", 410, 40, 380, 120)
        self.ip_log = self._frame("IP Tracker", "#ffaa00", 10, 170, 780, 120)
        self.codex_output = self._frame("Codex Feedback", "#00ff88", 10, 300, 780, 160)

    def _frame(self, title, color, x, y, w, h):
        frame = tk.LabelFrame(self.root, text=title, font=("Consolas", 9),
                              fg=color, bg="#1a1c20", bd=2, padx=4, pady=4)
        frame.place(x=x, y=y, width=w, height=h)
        text = tk.Text(frame, font=("Consolas", 8), bg="#0f1115", fg=color)
        text.pack(fill=tk.BOTH, expand=True)
        return text

    def _listbox(self, title, color, x, y, w, h):
        frame = tk.LabelFrame(self.root, text=title, font=("Consolas", 9),
                              fg=color, bg="#1a1c20", bd=2, padx=4, pady=4)
        frame.place(x=x, y=y, width=w, height=h)
        box = tk.Listbox(frame, font=("Consolas", 8), bg="#0f1115", fg=color)
        box.pack(fill=tk.BOTH, expand=True)
        return box

    def launch_interface(self):
        self.root.after(100, self._heartbeat)
        self.root.mainloop()

    def update_ip_log(self, ip_info):
        line = f"{ip_info['ip']} → {ip_info.get('city', '')}, {ip_info.get('country', '')} [{ip_info.get('org', '')}]\n"
        self.ip_log.insert(tk.END, line)
        self.ip_log.see(tk.END)

    def update_codex(self, feedback):
        self.codex_output.insert(tk.END, feedback + "\n")
        self.codex_output.see(tk.END)

    def update_threats(self, threat_info):
        self.threat_log.insert(tk.END, threat_info + "\n")
        self.threat_log.see(tk.END)

    def update_personas(self, personas):
        self.persona_display.delete(0, tk.END)
        for p in personas:
            self.persona_display.insert(tk.END, f"> {p}")

    def _heartbeat(self):
        self.root.after(1000, self._heartbeat)

