import tkinter as tk

def render_dashboard(feedback, votes):
    root = tk.Tk()
    root.title("Swarm Dashboard")
    root.geometry("600x300")
    tk.Label(root, text=feedback, font=("Consolas", 14), fg="lime", bg="black").pack(fill="x")

    frame = tk.Frame(root)
    frame.pack(pady=10)
    for node, vote in votes.items():
        color = "green" if vote else "red"
        tk.Label(frame, text=node, bg=color, width=10).pack(side="left", padx=5)

    root.after(3000, root.destroy)
    root.mainloop()

