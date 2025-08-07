# queen_core.py
import time
from queen_encryptor import Encryptor
from queen_defender import Defender
from queen_anomaly import AnomalyDetector
from queen_telemetry import TelemetryMixer
from queen_purger import VaultPurger
from queen_mutator import Mutator
from queen_visualizer import Visualizer
from queen_gui import launch_gui
from queen_sentinel import SwarmSentinel
from queen_manifest import Manifest

class QueenCore:
    def __init__(self):
        self.encryptor = Encryptor()
        self.defender = Defender()
        self.anomaly = AnomalyDetector()
        self.telemetry = TelemetryMixer()
        self.purger = VaultPurger()
        self.mutator = Mutator()
        self.visualizer = Visualizer()
        self.sentinel = SwarmSentinel()
        self.manifest = Manifest()
        self.audit_log = []

    def initialize(self):
        self.manifest.register_module("queen_core", "queen_core.py", version="6.0")
        self.audit_log.append("glyph(core:init)")
        print("QUEEN Protocol initialized.")

    def run_defense_cycle(self):
        self.encryptor.generate_key("cycle_key")
        self.purger.add_to_vault("cycle_key", "temp_data", ttl=5)
        self.defender.scan_quick()
        self.sentinel.deploy_agent("A1", "threat.exe")
        self.sentinel.neutralize_threat("A1")

        real = self.telemetry.generate_fake_stream()
        fake = self.telemetry.generate_fake_stream()
        blended = self.telemetry.blend_streams(real, fake)
        self.anomaly.train(blended)
        self.anomaly.detect(blended)

        self.mutator.mutate_block("scan")
        self.purger.check_and_purge()

        overlay = self.visualizer.render_overlay(
            self.encryptor.get_audit_log() +
            self.defender.get_audit_log() +
            self.anomaly.get_audit_log() +
            self.purger.get_audit_log() +
            self.mutator.get_mutation_log()[-1:] +
            self.sentinel.get_audit_log(),
            self.sentinel.get_recent_fx()
        )

        for line in overlay:
            print(line)

        self.audit_log.append("glyph(core:cycle)")

    def launch_gui(self):
        launch_gui()

    def get_audit_log(self):
        return self.audit_log[-5:]

