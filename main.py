# -*- coding: utf-8 -*-
import display
import embedded
import time
import signal
import os
import sys
import pyqtgraph as pg
from PyQt5 import QtCore, QtWidgets


# This forces the application to render directly to the LCD driver.
os.environ['QT_QPA_PLATFORM'] = 'linuxfb'

app = display.QtWidgets.QApplication([])
main_window = display.MainWindow(embedded.control.QCM_FREQUENCY_SAMPLE_SIZE) #SET NUMBER to max data size
main_window.setWindowFlags(display.QtCore.Qt.CustomizeWindowHint)
main_window.showMaximized()

class __main__:

    __is_running=False
    __buffer_measurement=None
    __sample_measurement=None
    __result=False

    __MEASUREMENT_TOLERANCE=1000

    embedded_interaction=None
    stages=[]
    current_stage=1

    __event_drain_necessary=False
    
    app = None
    main_window = None

    def __init__(self):
        signal.signal(signal.SIGTERM, self.application_stop) 
        signal.signal(signal.SIGINT, self.application_stop)
        
        self.embedded_interaction = embedded.control(self.next_stage)

        self.__is_running=True
        self.stages=[self.start, self.measure_nothing, self.measure_buffer, self.measure_sample, self.clean]     


    def run(self):
        try:
            
            self.stages[0]()
            while(self.__is_running):
                if(self.__event_drain_necessary):
                    self.embedded_interaction.drain_and_enable_button(self.next_stage)
                    self.__event_drain_necessary=False

                time.sleep(1)
        except Exception as error:
            print(error)
            
    def next_stage(self, button=None):
        self.embedded_interaction.disable_button()
        self.stages[self.current_stage]() #Runs the stored function
        self.current_stage=(self.current_stage+1)%len(self.stages)
        self.__event_drain_necessary=True

    def start(self):
        print("Please press button for control measurement solution, then press the button")
        #display.display.display_buffer_next()
        main_window.show_text("Please press button for control measurement solution, then press the button")

    def measure_nothing(self):
        print("Measuring nothing... For maintenance?")
        nothing_measurement=self.embedded_interaction.measure_frequency()
        print(nothing_measurement)
        #display.display.display_graph()
        main_window.show_graph()

    def measure_buffer(self):
        print("Measuring buffer solution, insert sample next, then press the button")
        #display.display.display_graph()
        main_window.show_graph()
        main_window.set_title("Measuring buffer...")

        self.__buffer_measurement=self.embedded_interaction.measure_frequency()

        #display.display.display_sample_next()
        main_window.show_text("Measurement done.  Switch to sample, then press the button.")

        

    def measure_sample(self):
        print ("Measuring sample solution, insert cleaning next, then press the button")
        #display.display.display_graph()
        main_window.show_graph()
        main_window.set_title("Measuring sample...")

        self.__sample_measurement=self.embedded_interaction.measure_frequency()
        self.__result=not(self.__buffer_measurement-self.__MEASUREMENT_TOLERANCE<self.__sample_measurement 
                          and self.__sample_measurement<self.__buffer_measurement+self.__MEASUREMENT_TOLERANCE)
        #display.display.display_cleaning_next()
        main_window.show_text("Measurement done.  Switch to cleaning solution, then press the button.")


    def clean(self):
        print("Cleaning the device, perepare next sample")
        #display.display.display_cleaning()
        main_window.show_text("Cleaning the device, perepare next sample")
        self.embedded_interaction.clean()
        print("Listeria: ", self.__result)
        #display.display.display_result(self.__result)
        main_window("Listeria: {self.__result}")

    def application_stop(self,sig,frame):
        self.__is_running=False
        
    def __del__(self):
        del self.embedded_interaction

# This forces the application to render directly to the LCD driver.
os.environ['QT_QPA_PLATFORM'] = 'linuxfb'
    


application_instance=__main__()
application_instance.run()

