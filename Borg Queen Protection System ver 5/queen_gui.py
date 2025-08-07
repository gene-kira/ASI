# queen_gui.py
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QPushButton, QTextEdit
)
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtCore import Qt
import sys

class MythicGUI(QWidget):
    def __init__(self, visualizer):
        super().__init__()
        self.visualizer = visualizer
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("QUEEN Protocol HUD")
        self.setGeometry(100, 100, 600, 400)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor("#1e1e2f"))
        palette.setColor(QPalette.WindowText, QColor("#f0f0ff"))
        self.setPalette(palette)

        layout = QVBoxLayout()

        self.fx_display = QTextEdit()
        self.fx_display.setReadOnly(True)
        self.fx_display.setStyleSheet("background-color: #2e2e3f; color: #ffccff; font-family: Consolas;")

        self.refresh_btn = QPushButton("🔄 Refresh HUD")
        self.refresh_btn.clicked.connect(self.update_display)

        layout.addWidget(QLabel("Mythic Audit & FX Overlay"))
        layout.addWidget(self.fx_display)
        layout.addWidget(self.refresh_btn)

        self.setLayout(layout)

    def update_display(self):
        audit = ["glyph(scan:quick)", "glyph(purge:temp_key)", "glyph(anomaly:3)"]
        fx = [
            {"burst": "flare", "color": "violet", "intensity": 15},
            {"burst": "nova", "color": "orange", "intensity": 25}
        ]
        overlay = self.visualizer.render_overlay(audit, fx)
        self.fx_display.setText("\n".join(overlay))

def launch_gui():
    app = QApplication(sys.argv)
    from queen_visualizer import Visualizer
    gui = MythicGUI(Visualizer())
    gui.show()
    sys.exit(app.exec_())

