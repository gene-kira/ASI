import tkinter as tk
from tkinter import ttk
import threading
import random
import time

class MagicBoxCloakNode:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🧙‍♂️ MagicBox Cloak Node")
        self.root.geometry("900x700")  # ✅ Wider window to fit full list

        self.status_label = tk.Label(self.root, text="Initializing...", font=("Consolas", 12), fg="white", bg="black")
        self.status_label.pack(pady=10)

        self.ip_list = tk.Listbox(self.root, height=10, width=110, font=("Consolas", 10))  # ✅ Wider listbox + monospace font
        self.ip_list.pack(pady=10)

        self.progress = ttk.Progressbar(self.root, orient="horizontal", length=800, mode="determinate")
        self.progress.pack(pady=10)

        self.swarm_canvas = tk.Canvas(self.root, width=800, height=300, bg="black")
        self.swarm_canvas.pack(pady=10)

        self.vault_label = tk.Label(self.root, text="Vault Status: 🔒 Sealed", font=("Consolas", 12), fg="cyan", bg="black")
        self.vault_label.pack(pady=10)

        self.mutation_trail = []

        self.start_threads()
        self.root.mainloop()

    def start_threads(self):
        threading.Thread(target=self.simulate_ip_mutation, daemon=True).start()
        threading.Thread(target=self.simulate_progress, daemon=True).start()
        threading.Thread(target=self.animate_swarm, daemon=True).start()
        threading.Thread(target=self.vault_cycle, daemon=True).start()

    def simulate_ip_mutation(self):
        while True:
            mutated_ip = f"{random.randint(10, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}.{random.randint(0, 255)}"
            mac = ":".join(f"{random.randint(0, 255):02x}" for _ in range(6))
            entry = f"🌀 IP: {mutated_ip} | MAC: {mac} | GeoIP: {random.choice(['🌍 Earth', '🪐 Mars', '🌑 Moon'])}"
            self.ip_list.insert(0, entry)
            if self.ip_list.size() > 10:
                self.ip_list.delete(10)
            self.status_label.config(text=f"Mutating → {mutated_ip}")
            self.mutation_trail.append(mutated_ip)
            time.sleep(2)

    def simulate_progress(self):
        while True:
            for i in range(101):
                self.progress["value"] = i
                time.sleep(0.05)
            for i in range(100, -1, -1):
                self.progress["value"] = i
                time.sleep(0.05)

    def animate_swarm(self):
        nodes = []
        for _ in range(20):
            x, y = random.randint(0, 800), random.randint(0, 300)
            node = self.swarm_canvas.create_oval(x, y, x+10, y+10, fill="cyan")
            nodes.append(node)

        while True:
            for node in nodes:
                dx, dy = random.randint(-5, 5), random.randint(-5, 5)
                self.swarm_canvas.move(node, dx, dy)
            self.swarm_canvas.update()
            time.sleep(0.1)

    def vault_cycle(self):
        while True:
            self.vault_label.config(text="Vault Status: 🔓 Rebirthing...", fg="orange")
            time.sleep(3)
            self.vault_label.config(text="Vault Status: 🔒 Sealed", fg="cyan")
            time.sleep(7)

if __name__ == "__main__":
    MagicBoxCloakNode()

