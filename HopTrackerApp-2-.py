import subprocess
import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox
import re
import socket

# Optional: Attempt theme setup
def apply_magicbox_theme(root):
    style = ttk.Style(root)
    try:
        root.tk.call("source", "azure.tcl")  # Azure theme file should be in the same directory
        style.theme_use("azure-dark")
    except:
        style.theme_use("clam")  # Fallback
    style.configure("TButton", font=("Segoe UI", 12), padding=10)
    style.configure("TLabel", font=("Segoe UI", 12))

def resolve_default_target():
    try:
        return socket.gethostbyname("www.microsoft.com")
    except:
        return "8.8.8.8"

def run_traceroute(destination):
    system_os = platform.system()
    command = ["tracert", "-d", destination] if system_os == "Windows" else ["traceroute", "-n", destination]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        output = result.stdout
        hops = 0
        hops_display = []

        for line in output.splitlines():
            ip_match = re.findall(r"\d+\.\d+\.\d+\.\d+", line)
            if ip_match:
                hops += 1
                hops_display.append(f"🌀 Hop {hops}: {ip_match[0]}")
            elif system_os == "Windows" and line.strip().startswith(str(hops + 1)):
                hops += 1
                hops_display.append(f"🌀 Hop {hops}: {line.strip()}")

        return f"🔍 Tracing to {destination}...\n\n" + "\n".join(hops_display) + f"\n\n🚀 Total Hops: {hops}", hops
    except Exception as e:
        return f"❌ Error: {str(e)}", 0

class MagicBoxTracerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("🧙‍♂️ MagicBox Hop Tracker")
        self.root.geometry("700x500")
        apply_magicbox_theme(self.root)
        self.build_gui()

    def build_gui(self):
        ttk.Label(self.root, text="Enter Destination (or leave blank):").pack(pady=10)
        self.entry = ttk.Entry(self.root, font=("Segoe UI", 12))
        self.entry.pack(pady=5, padx=20, fill=tk.X)

        self.trace_btn = ttk.Button(self.root, text="🕵️ Trace Route", command=self.start_trace)
        self.trace_btn.pack(pady=15)

        self.output_text = tk.Text(self.root, wrap="word", font=("Consolas", 11))
        self.output_text.pack(expand=True, fill=tk.BOTH, padx=20, pady=10)

    def start_trace(self):
        dest = self.entry.get().strip() or resolve_default_target()
        self.trace_btn.config(state=tk.DISABLED)
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=self.trace_and_display, args=(dest,), daemon=True).start()

    def trace_and_display(self, dest):
        result, _ = run_traceroute(dest)
        self.output_text.insert(tk.END, result)
        self.trace_btn.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxTracerGUI(root)
    root.mainloop()

