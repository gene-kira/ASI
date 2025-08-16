import yaml, os

class ConfigLoader:
    def __init__(self, path="magicbox_config.yaml"):
        self.path = path
        self.config = self.load_config()

    def load_config(self):
        if not os.path.exists(self.path):
            raise FileNotFoundError("Config file missing.")
        with open(self.path, 'r') as f:
            return yaml.safe_load(f)

