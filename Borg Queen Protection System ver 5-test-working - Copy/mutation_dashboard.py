# mutation_dashboard.py
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QTextEdit, QGraphicsView, QGraphicsScene
from PyQt5.QtGui import QFont, QColor
from PyQt5.QtCore import Qt, QTimer
import sys

class MutationDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("🧿 Mutation Dashboard")
        self.setGeometry(100, 100, 1200, 800)
        self.setStyleSheet("background-color: #0f0f1a; color: #e0e0ff;")

        layout = QVBoxLayout()

        self.title = QLabel("🧬 Real-Time Mutation FX")
        self.title.setFont(QFont("Consolas", 20))
        self.title.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.title)

        self.fx_view = QGraphicsView()
        self.fx_scene = QGraphicsScene()
        self.fx_view.setScene(self.fx_scene)
        self.fx_view.setStyleSheet("background-color: #1a1a2e; border: 2px solid #444;")
        layout.addWidget(self.fx_view)

        self.log_console = QTextEdit()
        self.log_console.setReadOnly(True)
        self.log_console.setFont(QFont("Courier", 12))
        self.log_console.setStyleSheet("background-color: #111; color: #0ff;")
        layout.addWidget(self.log_console)

        self.setLayout(layout)

        # Simulate log updates
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_logs)
        self.timer.start(1000)

    def update_logs(self):
        self.log_console.append("🌀 Agent alpha mutated → scan_and_purge")
        self.log_console.append("💥 Purge daemon triggered in vault:core")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    dashboard = MutationDashboard()
    dashboard.show()
    sys.exit(app.exec_())

