# main.py

import threading
from gui import RealTimeESD
from utils import log_codex

def launch():
    app = RealTimeESD()
    app.after(1000, lambda: log_codex("🔥 Auto-start complete. All systems defending."))
    app.mainloop()

if __name__ == "__main__":
    threading.Thread(target=launch).start()

