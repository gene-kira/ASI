# MagicBox Hop Tracker - One Click GUI
import subprocess
import platform
import threading
import tkinter as tk
from tkinter import ttk, messagebox

# Auto Theme Setup for MagicBox Edition
def apply_magicbox_theme(root):
    style = ttk.Style(root)
    root.tk.call("source", "azure.tcl")  # Optional: Azure theme file if available
    style.theme_use("azure-dark") if "azure-dark" in style.theme_names() else None
    style.configure("TButton", font=("Segoe UI", 12), padding=10)
    style.configure("TLabel", font=("Segoe UI", 12))

# Core traceroute logic
def run_traceroute(destination):
    system_os = platform.system()
    if system_os == "Windows":
        command = ["tracert", "-d", destination]
    else:
        command = ["traceroute", destination]

    try:
        result = subprocess.run(command, capture_output=True, text=True)
        hops = 0
        for line in result.stdout.splitlines():
            if line.strip().isdigit():
                hops += 1
            elif line.strip().startswith("  "):  # On Windows, hop lines start with spaces
                hops += 1
        return result.stdout, hops
    except Exception as e:
        return str(e), 0

# GUI setup
class HopTrackerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("🧙 MagicBox Hop Tracker")
        self.root.geometry("600x400")
        apply_magicbox_theme(self.root)

        self.build_gui()

    def build_gui(self):
        ttk.Label(self.root, text="Enter Destination:").pack(pady=10)
        self.entry = ttk.Entry(self.root, font=("Segoe UI", 12))
        self.entry.pack(pady=5)

        self.button = ttk.Button(self.root, text="🕵️‍♂️ Track Hops", command=self.start_trace)
        self.button.pack(pady=20)

        self.output_text = tk.Text(self.root, height=10, font=("Consolas", 10), wrap="word")
        self.output_text.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    def start_trace(self):
        destination = self.entry.get().strip()
        if not destination:
            messagebox.showerror("Error", "Please enter a valid destination address.")
            return
        self.button.config(state=tk.DISABLED)
        self.output_text.delete("1.0", tk.END)
        threading.Thread(target=self.trace_and_display, args=(destination,), daemon=True).start()

    def trace_and_display(self, destination):
        result, hops = run_traceroute(destination)
        self.output_text.insert(tk.END, f"Destination: {destination}\n")
        self.output_text.insert(tk.END, f"Estimated Hops: {hops}\n\n{result}")
        self.button.config(state=tk.NORMAL)

if __name__ == "__main__":
    root = tk.Tk()
    app = HopTrackerApp(root)
    root.mainloop()

