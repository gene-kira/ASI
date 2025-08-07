# fx_engine.py
from PyQt5.QtWidgets import QGraphicsEllipseItem, QGraphicsTextItem
from PyQt5.QtGui import QColor, QBrush, QPen, QFont
import random

class FXEngine:
    def render_glyph(self, mutation_text):
        x, y = random.randint(100, 1000), random.randint(100, 600)
        ellipse = QGraphicsEllipseItem(x, y, 40, 40)
        ellipse.setBrush(QBrush(QColor(0, 255, 180, 180)))
        ellipse.setPen(QPen(QColor(0, 255, 255), 2))

        label = QGraphicsTextItem(mutation_text)
        label.setDefaultTextColor(QColor(255, 255, 255))
        label.setFont(QFont("Consolas", 10))
        label.setPos(x - 20, y - 30)

        return [ellipse, label]

    def render_purge_burst(self, location, intensity):
        x, y = random.randint(100, 1000), random.randint(100, 600)
        size = int(60 * intensity)
        burst = QGraphicsEllipseItem(x, y, size, size)
        burst.setBrush(QBrush(QColor(255, 0, 0, 180)))
        burst.setPen(QPen(QColor(255, 100, 100), 3))

        label = QGraphicsTextItem(f"💥 {location}")
        label.setDefaultTextColor(QColor(255, 200, 200))
        label.setFont(QFont("Consolas", 10))
        label.setPos(x - 20, y - 30)

        return [burst, label]

    def render_aura_ring(self, agent_name, activity_level):
        x, y = random.randint(100, 1000), random.randint(100, 600)
        radius = int(30 + activity_level * 20)
        ring = QGraphicsEllipseItem(x, y, radius, radius)
        ring.setBrush(QBrush(QColor(0, 0, 0, 0)))
        ring.setPen(QPen(QColor(0, 255, 255, 150), 2))

        label = QGraphicsTextItem(agent_name)
        label.setDefaultTextColor(QColor(200, 255, 255))
        label.setFont(QFont("Consolas", 10))
        label.setPos(x, y - 20)

        return [ring, label]

