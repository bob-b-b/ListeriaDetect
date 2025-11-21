import display
import embedded
import keyboard
import time

class __main:

    __buffer_measurement=None
    __sample_measurement=None
    
    def main(self):
        is_running=True
        stages=[self.start, self.measure_buffer, self.measure_sample, self.clean]
        current_stage=1

        stages[0]()

        while(is_running):
            #if(keyboard.is_pressed('k')):
            if(embedded.gpio.is_button_pressed):
                time.sleep(2) #This is just the keypress debouncing, i think for the button it should be handeled in embedded class
                stages[current_stage]() #Runs the stored function
                current_stage=(current_stage+1)%len(stages)
            
        
    def start():
        print("Please input the buffer solution, then press the button")
        display.display.display_buffer_next()

    def measure_buffer(self):
        print("Measuring buffer solution, insert sample next, then press the button")
        display.display.display_graph()

        self.__buffer_measurement=embedded.control.measure_frequency()

        display.display.display_sample_next()

        

    def measure_sample(self):
        print ("Measuring sample solution, insert cleaning next, then press the button")
        display.display.display_graph()

        self.__sample_measurement=embedded.control.measure_frequency()

        display.display.display_cleaning_next()


    def clean():
        print("Cleaning the device, perepare next sampe")
        display.display.display_cleaning()
        embedded.control.clean()
        display.display.display_result()

    
__main.main()