from datetime import datetime
class MythicNarrator:
    def __init__(self, log_widget):
        self.log_widget = log_widget
    def log(self, event):
        msg = f"[{datetime.now().strftime('%H:%M:%S')}] {event}\n"
        self.log_widget.insert("end", msg)
        self.log_widget.see("end")
    def warn(self, msg):
        self.log(f"[WARNING] {msg}")

