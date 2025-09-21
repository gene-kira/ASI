from tkinter import Tk
from gui import CognitionLab
from browser import setup_browser
from storage import load_memory

if __name__ == "__main__":
    driver = setup_browser()
    log = load_memory()
    root = Tk()
    app = CognitionLab(root, driver, log)
    root.protocol("WM_DELETE_WINDOW", lambda: (driver.quit(), root.destroy()))
    root.mainloop()

