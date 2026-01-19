from PyQt5 import QtCore, QtWidgets
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, time_range):
        super().__init__()

        #Frequency Plot
        pg.setConfigOption('background', 'k')
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.hide()
        self.plot_graph.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.plot_graph.setTitle("Frequency Over Time", color="w", size="20pt") #MAKE TITLE CHANGEABLE IN A METHOD
        styles = {"color": "white", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Frequency (unit)", **styles)
        self.plot_graph.setLabel("bottom", "Time (unit)", **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        self.plot_graph.setXRange(0, 10)
        
        self.setCentralWidget(self.plot_graph)
        
        self.time = time_range
        self.buffer = []
        self.sample = []

        pen = pg.mkPen(color=(100, 255, 255))
        self.bufferline = self.plot_graph.plot(
            range(1, len(self.buffer) + 1),
            self.buffer,
            name="Buffer",
            pen=pen,
        )

        pen = pg.mkPen(color=(255, 255, 100))
        self.sampleline = self.plot_graph.plot(
            range(1, len(self.sample) + 1),
            self.sample,
            name="Sample",
            pen=pen,
        )
        
        self.plot_graph.showMaximized()
        
    def show_text(self, text):
        self.plot_graph.setTitle(text, color="w", size="20pt")
        
        
app = QtWidgets.QApplication([])
main = MainWindow(10)
main.show()
main.show_text("testing")
app.exec()