# watcher.py

from watchdog.events import FileSystemEventHandler

class PDPWatcher(FileSystemEventHandler):
    def __init__(self, log_callback, enhance_callback):
        self.log = log_callback
        self.enhance = enhance_callback

    def on_modified(self, event):
        if event.src_path.endswith(".py") and "personal_data_protector" in event.src_path:
            self.log(f"🔍 File modified: {event.src_path}")
            self.enhance(event.src_path)

