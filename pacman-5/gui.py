# gui.py
import tkinter as tk
from tkinter import ttk, filedialog
import threading
import config
from scanner import live_data_scan
from mixer import asi_mixer
from mutator import should_mutate, generate_mutated_code
from saver import save_memory, save_mutation
from replicator import sync_mutations
from voice import narrate_fusion, narrate_mutation, narrate_swarm_sync
from discovery import broadcast_presence, listen_for_nodes

memory_log = []
fusion_output = []
save_path = None

class MagicBoxGUI:
    def __init__(self, root, swarm_path=None):
        self.root = root
        self.swarm_path = swarm_path
        root.title("🧠 MagicBox ASI Interface")
        root.geometry("1000x800")

        self.selected_style = tk.StringVar(value="curious")
        self.status_text = tk.StringVar(value="🧠 Status: Initializing")
        self.scan_interval = tk.IntVar(value=60)

        ttk.Label(root, text="MagicBox Sentient Dashboard", font=("Helvetica", 16)).pack(pady=10)

        # Controls
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        ttk.Button(self.control_frame, text="📁 Select Save Location", command=self.select_save_location).grid(row=0, column=0, padx=5)
        ttk.Button(self.control_frame, text="💾 Save Knowledge", command=self.save_knowledge).grid(row=0, column=1, padx=5)
        ttk.Button(self.control_frame, text="🔊 Toggle Voice", command=self.toggle_voice).grid(row=0, column=2, padx=5)

        ttk.Label(self.control_frame, text="Mutation Style:").grid(row=0, column=3, padx=5)
        ttk.Combobox(self.control_frame, textvariable=self.selected_style,
                     values=["curious", "aggressive", "minimalist", "chaotic", "symbiotic"],
                     state="readonly", width=12).grid(row=0, column=4, padx=5)

        ttk.Button(self.control_frame, text="🧹 Clear List", command=self.clear_list).grid(row=0, column=5, padx=5)

        ttk.Label(self.control_frame, text="Scan Interval (sec):").grid(row=1, column=0, padx=5)
        ttk.Scale(self.control_frame, from_=10, to=300, variable=self.scan_interval,
                  orient="horizontal", command=self.update_scan_label).grid(row=1, column=1, columnspan=2, padx=5)
        self.freq_value_label = ttk.Label(self.control_frame, text=f"{self.scan_interval.get()} sec")
        self.freq_value_label.grid(row=1, column=3, padx=5)

        # Status
        ttk.Label(root, textvariable=self.status_text, relief=tk.SUNKEN, anchor="w", font=("Helvetica", 10)).pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

        # Event log
        self.list_frame = tk.Frame(root)
        self.list_frame.pack(pady=10, fill=tk.BOTH, expand=True)
        self.event_list = tk.Listbox(self.list_frame, height=15, width=120)
        self.event_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        ttk.Scrollbar(self.list_frame, orient="vertical", command=self.event_list.yview).pack(side=tk.RIGHT, fill=tk.Y)
        self.event_list.config(yscrollcommand=self.event_list.yview)

        # Swarm dashboard
        self.swarm_frame = tk.Frame(root)
        self.swarm_frame.pack(pady=10, fill=tk.X)

        ttk.Label(self.swarm_frame, text="🕸️ Swarm Nodes").pack(anchor="w")
        self.node_list = tk.Listbox(self.swarm_frame, height=5, width=50)
        self.node_list.pack(side=tk.LEFT, padx=10)

        ttk.Label(self.swarm_frame, text="🔔 Sync Alerts").pack(anchor="w")
        self.sync_log = tk.Listbox(self.swarm_frame, height=5, width=70)
        self.sync_log.pack(side=tk.LEFT, padx=10)

        broadcast_presence()
        listen_for_nodes(self.register_node)

        self.auto_start()

    def register_node(self, node_info):
        self.node_list.insert(tk.END, node_info)

    def sync_alert(self, mutation_info):
        self.sync_log.insert(tk.END, f"🔔 {mutation_info}")

    def clear_list(self):
        self.event_list.delete(0, tk.END)

    def toggle_voice(self):
        config.VOICE_ENABLED = not config.VOICE_ENABLED
        state = "ON" if config.VOICE_ENABLED else "OFF"
        self.event_list.insert(tk.END, f"🔊 Voice narration turned {state}")

    def update_scan_label(self, value):
        self.freq_value_label.config(text=f"{int(float(value))} sec")

    def auto_start(self):
        self.event_list.insert(tk.END, "🧠 Autonomous scan loop started")
        self.schedule_scan()

    def schedule_scan(self):
        interval_ms = self.scan_interval.get() * 1000
        self.root.after(interval_ms, self.run_live_scan)

    def run_live_scan(self):
        global memory_log, fusion_output

        if len(memory_log) > 500:
            memory_log = memory_log[-500:]

        live_memory = live_data_scan()
        memory_log.extend(live_memory)
        fusion_output = asi_mixer(live_memory)

        self.event_list.insert(tk.END, f"✅ Scan: {len(live_memory)} items tagged")
        self.event_list.insert(tk.END, f"🧪 Fusion: {len(fusion_output)} insights generated")
        narrate_fusion(fusion_output)

        avg_density = sum(item['weight'] for item in live_memory) / len(live_memory) if live_memory else 0
        self.status_text.set(f"🧠 Density: {int(avg_density)} | 🔁 Swarm Sync: Pending")

        personality = {
            "node_id": hash(save_path) % 9999 if save_path else 0,
            "mutation_style": self.selected_style.get(),
            "curiosity_bias": 75,
            "density_threshold": 60,
            "novelty_threshold": 90
        }

        if should_mutate(live_memory, personality):
            code, mutation_id = generate_mutated_code(live_memory, personality)
            if save_mutation(code, mutation_id, save_path):
                self.event_list.insert(tk.END, f"🧬 Mutation {mutation_id} saved")
                narrate_mutation(mutation_id)
                if self.swarm_path:
                    sync_mutations(save_path, self.swarm_path, alert_callback=self.sync_alert)
                    self.status_text.set(f"🧠 Density: {int(avg_density)} | 🔁 Swarm Sync: Complete")

        self.schedule_scan()

    def select_save_location(self):
        global save_path
        save_path = filedialog.askdirectory()
        if save_path:
            self.event_list.insert(tk.END, f"📁 Save location set: {save_path}")

    def save_knowledge(self):
        if save_memory(memory_log, fusion_output, save_path):
            self.event_list.insert(tk.END, "💾 Knowledge saved")
        else:
            self.event_list.insert(tk.END, "⚠️ Save failed")

    def get_save_path(self):
        return save_path

