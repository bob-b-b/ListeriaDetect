from PyQt5.QtCore import QObject, pyqtSignal

class ScreenSignals(QObject):
    # When this is emitted, it tells the GUI to run showgraph
    trigger_graph = pyqtSignal()
    trigger_text = pyqtSignal(str)

    add_value = pyqtSignal(float)


# Create one shared instance to be used everywhere
shared_msg = ScreenSignals()