# codex_monitor_shell_pyqt_scaled.py

import sys
import socket
import threading
import json
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QTextEdit, QGridLayout, QVBoxLayout, QHBoxLayout, QFrame
)
from PyQt5.QtGui import QFont, QPainter, QColor, QPen
from PyQt5.QtCore import Qt

HOST = 'localhost'
PORT = 24660

class GlyphWidget(QWidget):
    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        pen = QPen(QColor("lime"), 2)
        painter.setPen(pen)
        for i in range(3):
            x = 45 + i * 45
            painter.drawEllipse(x, 8, 30, 30)
            painter.drawLine(x + 15, 8, x + 15, 38)
            painter.drawLine(x, 23, x + 30, 23)

class CodexMonitorGUI(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Codex Monitor Daemon V.IXI-F.2466")
        self.setStyleSheet("background-color: black; color: lime;")
        self.setGeometry(100, 100, 1050, 675)

        self.layout = QVBoxLayout()
        self.setLayout(self.layout)

        self.draw_header()
        self.draw_panels()
        threading.Thread(target=self.listen_for_data, daemon=True).start()

    def draw_header(self):
        header_layout = QHBoxLayout()

        codex_label = QLabel("Codex Systems")
        codex_label.setFont(QFont("Consolas", 12, QFont.Bold))
        codex_label.setStyleSheet("color: lime;")

        daemon_label = QLabel("Codex Monitor Daemon V.IXI-F.2466")
        daemon_label.setFont(QFont("Consolas", 12))
        daemon_label.setStyleSheet("color: lime;")

        asi_label = QLabel("ASI Oversight")
        asi_label.setFont(QFont("Consolas", 12, QFont.Bold))
        asi_label.setStyleSheet("color: lime;")

        glyphs = GlyphWidget()
        glyphs.setFixedHeight(45)

        header_layout.addWidget(codex_label)
        header_layout.addStretch()
        header_layout.addWidget(glyphs)
        header_layout.addStretch()
        header_layout.addWidget(asi_label)

        self.layout.addLayout(header_layout)

    def draw_panels(self):
        grid = QGridLayout()
        self.text_widgets = {}

        titles = [
            "Registry Watchdog", "Process Mapper", "Flip-Flop Detector",
            "Sync Overlay", "Live Log Viewer", "Persona", "Event Feed"
        ]

        positions = [(i // 3, i % 3) for i in range(len(titles))]

        for title, (row, col) in zip(titles, positions):
            panel = self.create_panel(title)
            grid.addLayout(panel, row, col)

        self.layout.addLayout(grid)

    def create_panel(self, title):
        layout = QVBoxLayout()
        frame = QFrame()
        frame.setStyleSheet("border: 2px solid lime; background-color: black;")
        frame_layout = QVBoxLayout()
        frame.setLayout(frame_layout)

        label = QLabel(title)
        label.setFont(QFont("Consolas", 9, QFont.Bold))
        label.setStyleSheet("color: cyan;")
        text_edit = QTextEdit()
        text_edit.setFont(QFont("Consolas", 8))
        text_edit.setStyleSheet("background-color: black; color: lime; border: none;")
        frame_layout.addWidget(label)
        frame_layout.addWidget(text_edit)

        layout.addWidget(frame)
        self.text_widgets[title] = text_edit
        return layout

    def listen_for_data(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind((HOST, PORT))
            s.listen()
            while True:
                conn, _ = s.accept()
                with conn:
                    data = conn.recv(65536)
                    if data:
                        self.update_gui(json.loads(data.decode()))

    def update_gui(self, payload):
        self.update_panel("Registry Watchdog", payload.get('registry', []), "[REG]")
        self.update_panel("Process Mapper", payload.get('process', []), "[PROC]")
        self.update_panel("Flip-Flop Detector", payload.get('flipflop', []), "[FLIP]")
        self.update_panel("Live Log Viewer", payload.get('registry', []) + payload.get('process', []), "[LOG]")
        self.update_panel("Event Feed", payload.get('network', []), "[NET]")

    def update_panel(self, title, data, prefix):
        panel = self.text_widgets.get(title)
        for item in data:
            if prefix == "[NET]":
                line = f"{prefix} {item['timestamp']} {item['direction']} {item['origin']} → {item['destination']}\n"
            else:
                line = f"{prefix} {item['key']} → {item.get('old')} → {item.get('new')}\n"
            panel.append(line)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = CodexMonitorGUI()
    gui.show()
    sys.exit(app.exec_())

