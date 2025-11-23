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

    
# sudo apt update
# sudo apt install python3-dev python3-pip python3-setuptools
# pip3 install RPi.GPIO -GPIO can only be installed on a Raspberry Pi OS.
# used to get data from the raspb.Pi pin.
class qcm:
    @staticmethod
    def get_qcm_frequency():
        import RPi.GPIO as GPIO
        QCM_PIN = 3  # Change to the actual QCM sensor pin we're using
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(QCM_PIN, GPIO.IN)
        # Read the sensor value
        value = GPIO.input(QCM_PIN)
        # we likely need to process 'value' to get the actual data, not sure how the sensor input looks like
        return value