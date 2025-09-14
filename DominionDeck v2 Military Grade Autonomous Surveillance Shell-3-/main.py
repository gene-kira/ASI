from PyQt5.QtWidgets import QApplication
from panel_threat import ThreatPanel
from panel_traffic import TrafficPanel
from panel_ports import PortMonitorPanel

if __name__ == "__main__":
    app = QApplication([])
    threat_panel = ThreatPanel()
    traffic_panel = TrafficPanel()
    port_panel = PortMonitorPanel()
    threat_panel.show()
    traffic_panel.show()
    port_panel.show()
    app.exec_()

