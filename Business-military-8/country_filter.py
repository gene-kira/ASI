# country_filter.py

class CountryFilter:
    def __init__(self, gui):
        self.gui = gui

    def allowed(self, content):
        """
        Checks if the content's origin matches the allowed country codes.
        Returns True if allowed, False if blocked.
        """
        allowed_countries = self.gui.country_filter.get().split(",")
        content_lower = content.lower()

        for code in allowed_countries:
            code = code.strip().lower()
            if f"origin: {code}" in content_lower:
                return True

        # If origin is specified and not allowed, block it
        if "origin:" in content_lower:
            return False

        # If no origin is specified, allow by default
        return True

