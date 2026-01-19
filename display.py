from PyQt5 import QtCore, QtWidgets
from pyqtgraph import PlotWidget, plot
import pyqtgraph as pg
import sys  # We need sys so that we can pass argv to QApplication
import os
from signals import shared_msg, MeasurementTypes

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self, time_range):
        super().__init__()

        shared_msg.trigger_graph.connect(self.show_graph)
        shared_msg.trigger_text.connect(self.show_text)
        shared_msg.add_value.connect(self.add_value)
        shared_msg.clear_data.connect(self.clear_data)        

        #Frequency Plot
        pg.setConfigOption('background', 'k')
        self.plot_graph = pg.PlotWidget()
        self.plot_graph.hide()
        self.plot_graph.setWindowFlags(QtCore.Qt.CustomizeWindowHint)
        self.plot_graph.setTitle("Frequency Over Time", color="k", size="20pt") #MAKE TITLE CHANGEABLE IN A METHOD
        styles = {"color": "red", "font-size": "18px"}
        self.plot_graph.setLabel("left", "Frequency (unit)", **styles)
        self.plot_graph.setLabel("bottom", "Time (unit)", **styles)
        self.plot_graph.addLegend()
        self.plot_graph.showGrid(x=True, y=True)
        #self.plot_graph.setXRange(0, 10)
        #self.plot_graph.setYRange(0, 10)
        self.setCentralWidget(self.plot_graph)

        self.time = time_range
        self.nothing = []
        self.buffer = []
        self.sample = []
        
        pen = pg.mkPen(color=(255, 100, 255))
        self.nothingline = self.plot_graph.plot(
            range(1, len(self.nothing) + 1),
            self.nothing,
            name="Nothing",
            pen=pen,
        )

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


#These methods update the graph itself
    def update_plot(self):
        self.nothingline.setData(range(1, len(self.nothing) + 1), self.nothing)
        self.bufferline.setData(range(1, len(self.buffer) + 1), self.buffer)
        self.sampleline.setData(range(1, len(self.sample) + 1), self.sample)

    def set_title(self, title):
        self.plot_graph.setTitle(title, color="w", size="20pt")


#These methods update the data used in the graph
    def add_value(self,value,type):
        if type==MeasurementTypes.NO_TYPE:
            if len(self.nothing) < self.time:
                self.buffer.append(value) #cut off values after time_range
            self.update_plot()
        if type==MeasurementTypes.BUFFER:
            if len(self.buffer) < self.time:
                self.buffer.append(value) #cut off values after time_range
            self.update_plot()
        if type==MeasurementTypes.SAMPLE:
            if len(self.sample) < self.time:
                self.sample.append(value) #cut off values after time_range
            self.update_plot()

    def clear_data(self):
        self.nothing = []
        self.buffer = []
        self.sample = []


#These methods switch between showing graph and instruction
    @QtCore.pyqtSlot(str)
    def show_text(self, text):
        self.plot_graph.setTitle(text, color="w", size="20pt")

    @QtCore.pyqtSlot()
    def show_graph(self):
        self.plot_graph.setTitle("Frequency Over Time", color="k", size="20pt")
        self.plot_graph.showMaximized()
        
    