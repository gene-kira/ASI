# gui.py — Tabbed GUI with Mutation Tree + Lockdown Dashboard
import tkinter as tk
from tkinter import ttk

class TacticalGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("SentinelNode Interface")
        self.root.geometry("1000x600")
        self.root.configure(bg="#0f1115")
        self._build_tabs()

    def _build_tabs(self):
        notebook = ttk.Notebook(self.root)
        notebook.pack(fill=tk.BOTH, expand=True)

        self.threat_log = self._tab(notebook, "Threat Grid", "#ff4444")
        self.persona_display = self._list_tab(notebook, "Persona Timeline", "#00ffff")
        self.ip_log = self._tab(notebook, "IP Tracker", "#ffaa00")
        self.codex_output = self._tab(notebook, "Codex Feedback", "#00ff88")
        self.ancestry_output = self._tab(notebook, "Mutation Viewer", "#ff00ff")
        self.swarm_output = self._tab(notebook, "Swarm Sync", "#ff8800")
        self.lockdown_output = self._tab(notebook, "Lockdown Dashboard", "#ff0000")

    def _tab(self, notebook, title, color):
        frame = tk.Frame(notebook, bg="#1a1c20")
        notebook.add(frame, text=title)
        text = tk.Text(frame, font=("Consolas", 9), bg="#0f1115", fg=color)
        text.pack(fill=tk.BOTH, expand=True)
        return text

    def _list_tab(self, notebook, title, color):
        frame = tk.Frame(notebook, bg="#1a1c20")
        notebook.add(frame, text=title)
        box = tk.Listbox(frame, font=("Consolas", 9), bg="#0f1115", fg=color)
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

    def update_ancestry(self, ancestry_entry):
        self.ancestry_output.insert(tk.END, ancestry_entry + "\n")
        self.ancestry_output.see(tk.END)

    def update_swarm(self, vote):
        self.swarm_output.insert(tk.END, str(vote) + "\n")
        self.swarm_output.see(tk.END)

    def update_lockdown(self, message):
        self.lockdown_output.insert(tk.END, message + "\n")
        self.lockdown_output.see(tk.END)

    def _heartbeat(self):
        self.root.after(1000, self._heartbeat)

