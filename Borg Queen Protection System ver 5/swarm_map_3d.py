# swarm_map_3d.py
import pyqtgraph as pg
import pyqtgraph.opengl as gl
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
import numpy as np
import sys
import random

class SwarmMap3D:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.view = gl.GLViewWidget()
        self.view.setWindowTitle("🕸️ SwarmMap3D")
        self.view.setGeometry(100, 100, 1200, 800)
        self.view.setCameraPosition(distance=600)

        # Grid background
        grid = gl.GLGridItem()
        grid.scale(2, 2, 1)
        self.view.addItem(grid)

        # Agent glyphs
        self.agents = []
        for _ in range(20):
            x, y, z = random.randint(-100, 100), random.randint(-100, 100), random.randint(-50, 50)
            color = pg.glColor((0, 255, 255))
            agent = gl.GLScatterPlotItem(pos=np.array([[x, y, z]]), color=color, size=10)
            self.agents.append(agent)
            self.view.addItem(agent)

        # Timer for movement
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_agents)
        self.timer.start(1000)

    def update_agents(self):
        for agent in self.agents:
            dx, dy, dz = random.uniform(-5, 5), random.uniform(-5, 5), random.uniform(-2, 2)
            pos = agent.pos + np.array([[dx, dy, dz]])
            agent.setData(pos=pos)

    def run(self):
        self.view.show()
        sys.exit(self.app.exec_())

