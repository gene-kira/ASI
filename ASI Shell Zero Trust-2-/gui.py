# gui.py

import tkinter
from asi_core import add_to_allowlist, add_to_blocklist, mutate_persona
from vault import log_feed
from swarm import ip_feed, get_local_ips, geo_ip
from trust_engine import override_trust, calculate_trust_score
from symbolic_memory import get_memory_trace
from trust_state import ALLOWLIST, BLOCKLIST, PERSONA

def launch_gui():
    root = tkinter.Tk()
    root.title("ASI Shell: MagicBox Defense")
    root.geometry("475x550")
    root.configure(bg="#f0f0f0")

    # Title + Status
    tkinter.Label(root, text="ASI Shell", font=("Segoe UI", 14, "bold"), fg="#222", bg="#f0f0f0").grid(row=0, column=0, columnspan=3, pady=5)
    tkinter.Label(root, text="Status: Autonomous | ASI Active | IP Visualizer", font=("Segoe UI", 10), fg="#006400", bg="#f0f0f0").grid(row=1, column=0, columnspan=3)

    # Log Feed
    log_box = tkinter.Text(root, height=6, width=60, font=("Consolas", 9), bg="#ffffff", fg="#000000")
    log_box.grid(row=2, column=0, columnspan=3, padx=10, pady=5)

    # IP Entry + Buttons
    ip_entry = tkinter.Entry(root, font=("Segoe UI", 10), width=20)
    ip_entry.grid(row=3, column=0, padx=10, pady=5)

    tkinter.Button(root, text="Allow", command=lambda: add_to_allowlist(ip_entry.get()), bg="#00cc66", fg="#fff", font=("Segoe UI", 9, "bold")).grid(row=3, column=1)
    tkinter.Button(root, text="Block", command=lambda: add_to_blocklist(ip_entry.get()), bg="#cc0033", fg="#fff", font=("Segoe UI", 9, "bold")).grid(row=3, column=2)

    # Trust Override Panel
    tkinter.Label(root, text="Trust Override:", font=("Segoe UI", 10, "bold"), bg="#f0f0f0").grid(row=4, column=0, columnspan=3)
    override_entry = tkinter.Entry(root, font=("Segoe UI", 10), width=20)
    override_entry.grid(row=5, column=0, padx=10)
    tkinter.Button(root, text="Set Score", command=lambda: override_trust(override_entry.get(), 100), bg="#0033cc", fg="#fff", font=("Segoe UI", 9)).grid(row=5, column=1)
    tkinter.Button(root, text="Mutate Persona", command=lambda: mutate_persona(override_entry.get(), "override"), bg="#6600cc", fg="#fff", font=("Segoe UI", 9)).grid(row=5, column=2)

    # IP Lists
    ip_list_box = tkinter.Text(root, height=4, width=60, font=("Consolas", 9), bg="#e8f4ff", fg="#000000")
    ip_list_box.grid(row=6, column=0, columnspan=3, padx=10)

    # Map Canvas
    map_canvas = tkinter.Canvas(root, width=450, height=120, bg="#1e1e2f")
    map_canvas.grid(row=7, column=0, columnspan=3, padx=10, pady=5)

    def color_for_ip(ip):
        if ip in ALLOWLIST:
            return "green"
        elif ip in BLOCKLIST:
            return "red"
        else:
            return "yellow"

    def refresh_logs():
        log_box.delete("1.0", tkinter.END)
        for entry in log_feed[-20:]:
            log_box.insert(tkinter.END, entry + "\n")

        ip_list_box.delete("1.0", tkinter.END)
        ip_list_box.insert(tkinter.END, "[ALLOWLIST]\n" + "\n".join(ALLOWLIST) + "\n\n[BLOCKLIST]\n" + "\n".join(BLOCKLIST) + "\n\n[LOCAL NETWORK]\n")
        for ip in get_local_ips():
            ip_list_box.insert(tkinter.END, f"{ip}\n")

        map_canvas.delete("all")
        map_canvas.create_text(225, 10, text="IP Map Visualizer", fill="#00ffcc", font=("Segoe UI", 10, "bold"))
        for ip, data in ip_feed.items():
            geo = geo_ip(ip)
            x = int((geo["lon"] + 180) * 450 / 360)
            y = int((90 - geo["lat"]) * 120 / 180)
            color = color_for_ip(ip)
            map_canvas.create_oval(x-3, y-3, x+3, y+3, fill=color)
            map_canvas.create_text(x+5, y, text=geo["country"], anchor="w", fill="#ffffff", font=("Segoe UI", 7))

        root.after(3000, refresh_logs)

    refresh_logs()
    root.mainloop()

