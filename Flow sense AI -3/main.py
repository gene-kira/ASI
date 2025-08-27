# main.py

from tkinter import Tk
from dashboard import MagicBoxDashboard
from autoloader import autoload

# 🔄 Ensure all dependencies are loaded
autoload()

# 🚀 Launch the GUI
if __name__ == "__main__":
    root = Tk()
    app = MagicBoxDashboard(root)
    root.mainloop()

