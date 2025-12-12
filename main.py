# -*- coding: utf-8 -*-
import display
import embedded
import time
import signal
import sys

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
    
    def __init__(self):
        signal.signal(signal.SIGTERM, self.application_stop) 
        signal.signal(signal.SIGINT, self.application_stop)
        
        self.embedded_interaction = embedded.control(self.next_stage)

        self.__is_running=True
        self.stages=[self.start, self.measure_nothing, self.measure_buffer, self.measure_sample, self.clean]
        

        self.stages[0]()


    def run(self):
        try:
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
        print("Please input the buffer solution, then press the button")
        #display.display.display_buffer_next()

    def measure_nothing(self):
        print("Measuring nothing... For maintenance?")
        nothing_measurement=self.embedded_interaction.measure_frequency()
        print(nothing_measurement)
        #display.display.display_graph()

    def measure_buffer(self):
        print("Measuring buffer solution, insert sample next, then press the button")
        #display.display.display_graph()

        self.__buffer_measurement=self.embedded_interaction.measure_frequency()

        #display.display.display_sample_next()

        

    def measure_sample(self):
        print ("Measuring sample solution, insert cleaning next, then press the button")
        #display.display.display_graph()

        self.__sample_measurement=self.embedded_interaction.measure_frequency()
        self.__result=not(self.__buffer_measurement-self.__MEASUREMENT_TOLERANCE<self.__sample_measurement 
                          and self.__sample_measurement<self.__buffer_measurement+self.__MEASUREMENT_TOLERANCE)
        #display.display.display_cleaning_next()


    def clean(self):
        print("Cleaning the device, perepare next sample")
        #display.display.display_cleaning()
        self.embedded_interaction.clean()
        print("Listeria: ", self.__result)
        #display.display.display_result(self.__result)

    def application_stop(self,sig,frame):
        self.__is_running=False
        
    def __del__(self):
        del self.embedded_interaction

    
application_instance=__main__()
application_instance.run()
