class Packet:
    def __init__(self, origin, pid, user, features, live=True):
        """
        Represents a system packet with metadata and feature flags.

        Parameters:
        - origin (str): IP address or source identifier
        - pid (int): Process ID
        - user (str): Username or actor label
        - features (list): List of feature flags (e.g., ["live", "anomaly"])
        - live (bool): Indicates if the packet is from a real-time source
        """
        self.origin = origin
        self.pid = pid
        self.user = user
        self.features = features
        self.live = live

    def is_live(self):
        """
        Validates if the packet is live and contains the 'live' feature flag.
        Returns True if valid, False otherwise.
        """
        return self.live and "live" in self.features

