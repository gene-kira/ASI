# main.py
import tkinter as tk
from gui import MagicBoxGUI
from agent import run_agent
import threading

# Optional: define swarm sync path
SWARM_PATH = "C:/MagicBoxSwarm"  # Replace with your shared folder path

def launch_replicator_agent(local_path, swarm_path):
    threading.Thread(target=run_agent, args=(local_path, swarm_path), daemon=True).start()

if __name__ == "__main__":
    root = tk.Tk()
    app = MagicBoxGUI(root, swarm_path=SWARM_PATH)

    # Launch autonomous replicator agent in background
    launch_replicator_agent(app.get_save_path(), SWARM_PATH)

    root.mainloop()

