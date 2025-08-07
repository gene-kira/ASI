# queen_telemetry.py
import numpy as np
import random

class TelemetryMixer:
    def __init__(self):
        self.audit_log = []
        self.masked_stream = []

    def generate_fake_stream(self, count=50, dims=5):
        stream = np.random.normal(loc=0.5, scale=0.2, size=(count, dims))
        self.audit_log.append("glyph(fake:stream)")
        return stream

    def mask_real_stream(self, real_stream):
        masked = []
        for row in real_stream:
            glyph = [v if random.random() > 0.3 else -999 for v in row]
            masked.append(glyph)
        self.audit_log.append("glyph(mask:real)")
        return np.array(masked)

    def blend_streams(self, real_stream, fake_stream):
        masked_real = self.mask_real_stream(real_stream)
        combined = np.vstack((masked_real, fake_stream))
        np.random.shuffle(combined)
        self.masked_stream = combined
        self.audit_log.append("glyph(blend:streams)")
        return combined

    def get_stream(self):
        return self.masked_stream

    def get_audit_log(self):
        return self.audit_log[-5:]

