from PyQt5.QtCore import QObject, pyqtSignal
from enum import Enum

class AddTypes(Enum):
    NO_TYPE=0
    BUFFER=1
    SAMPLE=2

class ScreenSignals(QObject):
    # When this is emitted, it tells the GUI to run showgraph
    trigger_graph = pyqtSignal()
    trigger_text = pyqtSignal(str)

    add_value = pyqtSignal(float, AddTypes)

    clear_data = pyqtSignal()


# Create one shared instance to be used everywhere
shared_msg = ScreenSignals()