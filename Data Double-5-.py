# codex_gui_realtime.py

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QGridLayout,
    QScrollArea, QPushButton
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import QTimer
import sys, time
import queue
import networkx as nx
import matplotlib.pyplot as plt

# === Thread-safe queues for real-time data injection ===
live_event_queue = queue.Queue()
threat_event_queue = queue.Queue()

class ASIConsole(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Codex Sentinel: ASI Oversight Console")
        self.setGeometry(100, 100, 1600, 900)
        self.setStyleSheet("background-color: #0f1115; color: #00ffff;")
        self.init_ui()

    def init_ui(self):
        font = QFont("JetBrains Mono", 10)
        layout = QGridLayout()

        # Scrollable Panels
        self.ingest_scroll, self.ingest_panel = self.create_scrollable_panel("Ingest Monitor")
        self.threat_scroll, self.threat_panel = self.create_scrollable_panel("Threat Matrix")
        self.codex_scroll, self.codex_panel = self.create_scrollable_panel("Codex Editor")
        self.audit_scroll, self.audit_panel = self.create_scrollable_panel("Audit Controls")

        layout.addWidget(self.ingest_scroll, 0, 0)
        layout.addWidget(self.threat_scroll, 0, 1)
        layout.addWidget(self.codex_scroll, 1, 0)
        layout.addWidget(self.audit_scroll, 1, 1)

        # Codex Graph Button
        graph_button = QPushButton("Render Codex Mutation Graph")
        graph_button.setStyleSheet("background-color: #00ffff; color: #0f1115; font-weight: bold;")
        graph_button.clicked.connect(self.render_codex_graph)
        self.codex_panel.layout_ref.addWidget(graph_button)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Timers for real-time updates
        self.ingest_timer = QTimer()
        self.ingest_timer.timeout.connect(self.update_ingest_panel)
        self.ingest_timer.start(500)

        self.threat_timer = QTimer()
        self.threat_timer.timeout.connect(self.update_threat_panel)
        self.threat_timer.start(500)

    def create_scrollable_panel(self, title):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        panel = QWidget()
        panel.setStyleSheet("border: 2px solid #00ffff; padding: 10px;")
        layout = QVBoxLayout()
        layout.addWidget(QLabel(f"{title} Panel"))
        panel.setLayout(layout)
        panel.layout_ref = layout
        scroll.setWidget(panel)
        return scroll, panel

    def update_ingest_panel(self):
        while not live_event_queue.empty():
            event = live_event_queue.get()
            glyph = {"SYNC": "🔄", "QUARANTINE": "🛑", "PURGE": "🔥"}.get(event["action"], "❓")
            label = QLabel(f"{glyph} [{event['port']}] → {event['action'].upper()} @ {time.strftime('%H:%M:%S', time.localtime(event['timestamp']))}")
            label.setStyleSheet("color: #00ff88; font-family: JetBrains Mono;")
            self.ingest_panel.layout_ref.addWidget(label)
            self.prune_panel(self.ingest_panel.layout_ref)

    def update_threat_panel(self):
        while not threat_event_queue.empty():
            threat = threat_event_queue.get()
            signature = "⚠️" if threat["score"] > 75 else "✅"
            label = QLabel(f"{signature} [{threat['port']}] Score: {threat['score']} → {threat['trigger'].upper()} @ {time.strftime('%H:%M:%S', time.localtime(threat['timestamp']))}")
            color = "#ff4444" if threat["trigger"] == "quarantine" else "#00ff88"
            label.setStyleSheet(f"color: {color}; font-family: JetBrains Mono;")
            self.threat_panel.layout_ref.addWidget(label)
            self.prune_panel(self.threat_panel.layout_ref)

    def prune_panel(self, layout, max_entries=50):
        while layout.count() > max_entries:
            old_widget = layout.itemAt(1).widget()
            layout.removeWidget(old_widget)
            old_widget.deleteLater()

    def render_codex_graph(self):
        G = nx.DiGraph()
        G.add_node("Ingest")
        G.add_node("Classify")
        G.add_node("Score")
        G.add_node("Quarantine")
        G.add_node("Sync")
        G.add_node("Purge")
        G.add_edges_from([
            ("Ingest", "Classify"),
            ("Classify", "Score"),
            ("Score", "Quarantine"),
            ("Score", "Sync"),
            ("Score", "Purge")
        ])
        pos = nx.spring_layout(G)
        plt.figure(figsize=(8, 6))
        nx.draw(G, pos, with_labels=True, node_color='cyan', edge_color='gray', font_weight='bold')
        plt.title("Codex Mutation Graph")
        plt.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    console = ASIConsole()
    console.show()
    sys.exit(app.exec_())

