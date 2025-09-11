class FakeTelemetryShield:
    def inject(self):
        fake_data = {"cpu": "99%", "temp": "900C", "location": "Mars"}
        print(f"[TELEMETRY] Injected decoy: {fake_data}")
        return fake_data

