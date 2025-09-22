import threading, time
from tkinter import ttk, scrolledtext, filedialog, Entry, Button
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt
from network import start_sniff, dissect_packet
from browser import is_ad, skip_ad, inject_js
from storage import save_memory, export_logs
from ad_signature_tracker import load_signatures, save_signatures, track_signature

class CognitionLab:
    def __init__(self, root, driver, log):
        self.root = root
        self.driver = driver
        self.log = log
        self.whitelist = []
        self.entropy = []
        self.mutations = len(log)
        self.blocking = True
        self.stealth = False
        self.sock = None

        self.feed = scrolledtext.ScrolledText(root, wrap="word", width=60, height=40)
        self.feed.pack(side="left", fill="both", expand=True)

        self.filter = ttk.Combobox(root, values=["All", "blue", "green", "orange", "black"])
        self.filter.set("All")
        self.filter.pack()

        self.toggle_btn = Button(root, text="Turn OFF Ad Blocker", command=self.toggle_block)
        self.toggle_btn.pack()

        self.stealth_btn = Button(root, text="Enable Stealth Mode", command=self.toggle_stealth)
        self.stealth_btn.pack()

        self.whitelist_box = ttk.Combobox(root, values=self.whitelist)
        self.whitelist_box.pack()

        self.whitelist_entry = Entry(root)
        self.whitelist_entry.pack()

        Button(root, text="Add to Whitelist", command=self.add_whitelist).pack()
        Button(root, text="Export Logs", command=self.export_logs_gui).pack()

        self.chart = self.setup_chart()

        threading.Thread(target=self.ad_loop, daemon=True).start()
        self.root.after(1000, self.update)

    def setup_chart(self):
        fig, ax = plt.subplots(figsize=(6, 4))
        line, = ax.plot([], [], color='magenta')
        ax.set_ylim(0, 3)
        canvas = FigureCanvasTkAgg(fig, master=self.root)
        canvas.get_tk_widget().pack(side="right")
        return line, ax, canvas

    def toggle_block(self):
        self.blocking = not self.blocking
        state = "ON" if self.blocking else "OFF"
        self.toggle_btn.config(text=f"Turn {'OFF' if self.blocking else 'ON'} Ad Blocker")
        self.feed.insert("end", f"🛡️ Ad Blocker is now {state}.\n")

    def toggle_stealth(self):
        self.stealth = not self.stealth
        state = "ENABLED" if self.stealth else "DISABLED"
        self.stealth_btn.config(text=f"{'Disable' if self.stealth else 'Enable'} Stealth Mode")
        self.feed.insert("end", f"🕵️ Stealth Mode {state}.\n")

    def add_whitelist(self):
        domain = self.whitelist_entry.get().strip()
        if domain and domain not in self.whitelist:
            self.whitelist.append(domain)
            self.whitelist_box.config(values=self.whitelist)
            self.feed.insert("end", f"🧭 Whitelisted domain: {domain}\n")

    def ad_loop(self):
        while True:
            if self.blocking and is_ad(self.driver):
                skip_ad(self.driver)
                self.mutations += 1
                msg = f"[Mutation #{self.mutations}] Stream ad detected — skipping."
                self.feed.insert("end", msg + "\n")
                self.log.append({"type": "ad", "message": msg, "timestamp": time.time()})
                save_memory(self.log)
                self.driver.refresh()
                time.sleep(5)

            inject_js(self.driver, self.stealth)

            seen = load_signatures()
            new_sigs = track_signature(self.driver)
            diffs = [s for s in new_sigs if s not in seen]
            if diffs:
                self.feed.insert("end", f"🧬 New ad signature detected — {len(diffs)} mutations cataloged.\n")
                seen.extend(diffs)
                save_signatures(seen)

            time.sleep(2)

    def update(self):
        if not self.sock:
            self.sock = start_sniff()
        try:
            data = self.sock.recvfrom(65565)[0]
        except:
            return
        result = dissect_packet(data, self.whitelist)
        if result:
            msg, color, ent, label = result
            self.entropy.append(ent)

            if ent > 2.5 and not self.stealth:
                self.stealth = True
                self.stealth_btn.config(text="Disable Stealth Mode")
                self.feed.insert("end", "⚠️ Entropy spike detected — activating Stealth Mode.\n")

            if self.filter.get() == "All" or self.filter.get() == color:
                self.feed.insert("end", msg + "\n")
                self.feed.see("end")

            self.log.append({"type": label, "message": msg, "timestamp": time.time()})
            save_memory(self.log)

        self.update_chart()
        self.root.after(1000, self.update)

    def update_chart(self):
        line, ax, canvas = self.chart
        line.set_data(range(len(self.entropy)), self.entropy)
        ax.set_xlim(max(0, len(self.entropy) - 100), len(self.entropy))
        canvas.draw()

    def export_logs_gui(self):
        path = filedialog.asksaveasfilename(defaultextension=".bin", filetypes=[("Encrypted Archive", "*.bin")])
        if path:
            key = export_logs(self.log, path)
            self.feed.insert("end", f"📦 Logs exported to {path}\n🔐 Key saved to {path}.key\n")
