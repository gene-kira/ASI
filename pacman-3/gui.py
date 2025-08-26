# gui.py
import tkinter as tk
from tkinter import ttk, filedialog
import threading

from scanner import live_data_scan
from mixer import asi_mixer
from mutator import should_mutate, generate_mutated_code
from saver import save_memory, save_mutation
from replicator import sync_mutations
from voice import narrate_fusion, narrate_mutation, narrate_swarm_sync
from overlay import NeuralOverlay
from personality import generate_personality
import config

memory_log = []
fusion_output = []
save_path = None

class MagicBoxGUI:
    def __init__(self, root, swarm_path=None):
        self.root = root
        self.swarm_path = swarm_path
        root.title("🧠 MagicBox ASI Interface")
        root.geometry("900x750")
        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Tkinter-bound variables (must be after root init)
        self.selected_style = tk.StringVar(value="curious")
        self.status_text = tk.StringVar(value="🧠 Status: Idle")

        self.label = ttk.Label(root, text="MagicBox Sentient Dashboard", font=("Helvetica", 16))
        self.label.pack(pady=10)

        # Control panel
        self.control_frame = tk.Frame(root)
        self.control_frame.pack(pady=10)

        self.select_button = ttk.Button(self.control_frame, text="📁 Select Save Location", command=self.select_save_location)
        self.select_button.grid(row=0, column=0, padx=5)

        self.save_button = ttk.Button(self.control_frame, text="💾 Save Knowledge", command=self.save_knowledge)
        self.save_button.grid(row=0, column=1, padx=5)

        self.voice_button = ttk.Button(self.control_frame, text="🔊 Toggle Voice", command=self.toggle_voice)
        self.voice_button.grid(row=0, column=2, padx=5)

        self.style_label = ttk.Label(self.control_frame, text="Mutation Style:")
        self.style_label.grid(row=0, column=3, padx=5)

        self.style_dropdown = ttk.Combobox(self.control_frame, textvariable=self.selected_style,
                                           values=["curious", "aggressive", "minimalist", "chaotic", "symbiotic"],
                                           state="readonly", width=12)
        self.style_dropdown.grid(row=0, column=4, padx=5)

        self.clear_button = ttk.Button(self.control_frame, text="🧹 Clear Log", command=self.clear_log)
        self.clear_button.grid(row=0, column=5, padx=5)

        # Status bar
        self.status_bar = ttk.Label(root, textvariable=self.status_text, relief=tk.SUNKEN, anchor="w", font=("Helvetica", 10))
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM, ipady=2)

        # Log area
        self.log = tk.Text(root, height=12, width=110)
        self.log.pack(pady=10)

        # Overlay canvas
        self.overlay_frame = tk.Frame(root)
        self.overlay_frame.pack(pady=10, fill=tk.BOTH, expand=True)

        self.auto_start()

    def clear_log(self):
        self.log.delete("1.0", tk.END)

    def toggle_voice(self):
        config.VOICE_ENABLED = not config.VOICE_ENABLED
        state = "ON" if config.VOICE_ENABLED else "OFF"
        self.log.insert(tk.END, f"🔊 Voice narration turned {state}.\n")

    def auto_start(self):
        self.log.insert(tk.END, "🧠 Autonomous live scan initializing...\n")
        threading.Thread(target=self.run_live_scan).start()

    def run_live_scan(self):
        global memory_log, fusion_output
        live_memory = live_data_scan()
        memory_log.extend(live_memory)
        fusion_output = asi_mixer(live_memory)
        self.log.insert(tk.END, f"✅ Live scan complete. {len(live_memory)} items tagged.\n")
        self.log.insert(tk.END, f"🧪 ASI Mixer generated {len(fusion_output)} fusion insights.\n")

        narrate_fusion(fusion_output)
        self.visualize_overlay(live_memory + fusion_output)

        # Update status bar
        avg_density = sum(item['weight'] for item in live_memory) / len(live_memory) if live_memory else 0
        self.status_text.set(f"🧠 Density: {int(avg_density)} | 🔁 Swarm Sync: Pending")

        # Manual personality override from dropdown
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
                self.log.insert(tk.END, f"🧬 Mutation {mutation_id} saved to vault.\n")
                narrate_mutation(mutation_id)
                if self.swarm_path:
                    sync_mutations(save_path, self.swarm_path)
                    narrate_swarm_sync()
                    self.status_text.set(f"🧠 Density: {int(avg_density)} | 🔁 Swarm Sync: Complete")

    def select_save_location(self):
        global save_path
        save_path = filedialog.askdirectory()
        if save_path:
            self.log.insert(tk.END, f"📁 Save location set to: {save_path}\n")

    def save_knowledge(self):
        if save_memory(memory_log, fusion_output, save_path):
            self.log.insert(tk.END, "💾 Knowledge saved successfully.\n")
        else:
            self.log.insert(tk.END, "⚠️ Failed to save knowledge.\n")

    def visualize_overlay(self, memory):
        NeuralOverlay(self.overlay_frame, memory)

    def get_save_path(self):
        return save_path

