# overlay.py
import tkinter as tk
import random

class NeuralOverlay:
    def __init__(self, root, memory, mode="fusion"):
        for widget in root.winfo_children():
            widget.destroy()

        self.canvas = tk.Canvas(root, width=700, height=300, bg="black")
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.memory = memory
        self.mode = mode
        self.node_refs = []

        if mode == "fusion":
            self.draw_fusion()
        elif mode == "lineage":
            self.draw_lineage()

    def draw_fusion(self):
        for item in self.memory:
            x, y = random.randint(50, 650), random.randint(50, 250)
            density = item.get("symbolic_density", item.get("weight", 50))
            pulse_radius = 5 + int(density / 10)
            color = "#%02x%02x%02x" % (
                density * 2 % 255,
                item['novelty'] * 2 % 255,
                150
            )
            node = self.canvas.create_oval(x, y, x + pulse_radius, y + pulse_radius, fill=color)
            label = item.get('process') or f"Port {item.get('port')}" or item.get('type', 'Node')
            self.canvas.create_text(x + pulse_radius + 5, y, text=label, fill="white", anchor="w")

            if item.get("type") == "fusion":
                self.canvas.create_oval(x - 2, y - 2, x + pulse_radius + 2, y + pulse_radius + 2, outline="cyan")
                self.canvas.tag_bind(node, "<Button-1>", lambda e, data=item: self.expand_node(data))

    def draw_lineage(self):
        fusion_nodes = [m for m in self.memory if m.get("type") == "fusion"]
        x_base, y_base = 50, 50
        spacing = 60

        for i, node in enumerate(fusion_nodes):
            x = x_base + (i % 10) * spacing
            y = y_base + (i // 10) * spacing
            mutation_id = node.get("mutation", "???")
            density = node.get("symbolic_density", 50)
            pulse_radius = 5 + int(density / 10)
            color = "#%02x%02x%02x" % (density * 2 % 255, 100, 255)

            node_obj = self.canvas.create_oval(x, y, x + pulse_radius, y + pulse_radius, fill=color)
            self.canvas.create_text(x + pulse_radius + 5, y, text=f"Mutation {mutation_id}", fill="white", anchor="w")
            self.canvas.tag_bind(node_obj, "<Button-1>", lambda e, data=node: self.expand_node(data))

            # Simulate transfer arc
            if i > 0:
                prev_x = x_base + ((i - 1) % 10) * spacing
                prev_y = y_base + ((i - 1) // 10) * spacing
                self.canvas.create_line(prev_x, prev_y, x, y, fill="lime", dash=(4, 2))

    def expand_node(self, data):
        info = f"🧬 Mutation {data.get('mutation')}\nSource: {data.get('source_file')} + Port {data.get('source_port')}\nDensity: {data.get('symbolic_density')}"
        popup = tk.Toplevel()
        popup.title("Mutation Lineage")
        tk.Label(popup, text=info, font=("Helvetica", 12), justify="left").pack(padx=20, pady=20)

