# 🔍 core/analyzer.py — Flow Analyzer
class FlowAnalyzer:
    def __init__(self):
        self.active_flows = []

    def ingest(self, pulse):
        self.active_flows.append(pulse)

    def get_recent_flows(self, count=10):
        return self.active_flows[-count:]

    def clear_flows(self):
        self.active_flows = []

