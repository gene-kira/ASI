# event_bus.py

from datetime import datetime

class EventBus:
    def __init__(self):
        self.events = []

    def log(self, message):
        """
        Logs a system event with timestamp and returns symbolic narration.
        """
        timestamp = datetime.now().strftime("%H:%M:%S")
        narrated = self.narrate_event(timestamp, message)
        self.events.append({"timestamp": timestamp, "message": message})
        return narrated

    def narrate_event(self, ts, msg):
        """
        Converts raw event messages into symbolic, mythic-style feedback.
        """
        msg_lower = msg.lower()
        if "purge" in msg_lower:
            return f"[PURGE] {ts} — The data was judged. It was cast into fire."
        elif "persona" in msg_lower:
            return f"[PERSONA] {ts} — A mask was worn. The system walks among shadows."
        elif "sync" in msg_lower:
            return f"[SYNC] {ts} — The nodes whispered. The prophecy aligned."
        elif "blocked" in msg_lower:
            return f"[BLOCKED] {ts} — A gate was sealed. The origin was denied."
        elif "ingest" in msg_lower:
            return f"[INGEST] {ts} — A thread was woven. The codex expanded."
        else:
            return f"[EVENT] {ts} — The system stirred. A new glyph was etched."

    def export_log(self):
        """
        Returns the full event history.
        """
        return list(self.events)

    def latest(self, count=5):
        """
        Returns the latest N events.
        """

