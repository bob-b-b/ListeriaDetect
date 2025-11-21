#import qcm_data_collection
import time

class control:
    PUMP_GPIO=1
    BUTTON_GPIO=2

    __FREQUENCY_SAMPLE_SIZE=25
    __SECONDS_BETWEEN_SAMPLES=2

    __CLEANING_TIME_SECONDS=10
    
    def is_button_pressed(): #Make sure this accounts for bouncing
        raise NotImplementedError()
    
    def __start_pump():
        raise NotImplementedError()
    
    def __stop_pump():
        raise NotImplementedError()
    
    def measure_frequency(self):
        self.__start_pump()

        sample_sums=0
        for _ in len(range(self.__FREQUENCY_SAMPLE_SIZE)):
            sample_sums+=qcm.get_qcm_frequency()
            time.sleep(self.__SECONDS_BETWEEN_SAMPLES)

        self.__stop_pump()

    def clean(self):
        self.__start_pump()
        time.sleep(self.__CLEANING_TIME_SECONDS)
        self.__stop_pump()

    
class qcm:
    def get_qcm_frequency():
        raise NotImplementedError()