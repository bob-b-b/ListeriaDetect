#import qcm_data_collection
import time
import RPi.GPIO as GPIO 

class control:
    PUMP_GPIO=1
    PUMP_FORWARD_GPIO=2
    PUMP_BACKWARD_GPIO=3
    BUTTON_GPIO=12

    __QCM_FREQUENCY_SAMPLE_SIZE=4
    __SECONDS_BETWEEN_SAMPLES=2

    __CLEANING_TIME_SECONDS=10

    __PWM_DUTY_CYCLE=50
    __PWM_FREQUENCY=255

    __pump_pwm=None

    
    def __start_pump(self, reverse=False):
        if reverse:
            GPIO.output(self.PUMP_FORWARD_GPIO, GPIO.LOW)
            GPIO.output(self.PUMP_BACKWARD_GPIO, GPIO.HIGH)
        else:
            GPIO.output(self.PUMP_BACKWARD_GPIO, GPIO.LOW)
            GPIO.output(self.PUMP_FORWARD_GPIO, GPIO.HIGH)

        self.__pump_pwm.start(self.__PWM_DUTY_CYCLE)
    
    def __stop_pump(self):
        self.__pump_pwm.stop()

    def enable_button(self, callback_function):
        GPIO.add_event_detect(
            self.BUTTON_GPIO,
            GPIO.FALLING,
            callback=callback_function,
            bouncetime=200
        )

    def disable_button(self):
        GPIO.remove_event_detect(self.BUTTON_GPIO)
    
    def measure_frequency(self):
        self.__start_pump()

        sample_sums=0
        for _ in range(self.__QCM_FREQUENCY_SAMPLE_SIZE):
            sample_sums+=qcm.get_qcm_frequency()
            time.sleep(self.__SECONDS_BETWEEN_SAMPLES)

        self.__stop_pump()
        
        return sample_sums/self.__QCM_FREQUENCY_SAMPLE_SIZE

    def clean(self):
        self.__start_pump(reverse=True)
        time.sleep(self.__CLEANING_TIME_SECONDS)
        self.__stop_pump()

    def __init__(self, callback_function):
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.PUMP_GPIO, GPIO.OUT)
        self.__pump_pwm=GPIO.PWM(self.PUMP_GPIO, self.__PWM_FREQUENCY)

        GPIO.setup(self.PUMP_FORWARD_GPIO, GPIO.OUT)
        GPIO.setup(self.PUMP_BACKWARD_GPIO, GPIO.OUT)

        GPIO.setup(self.BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.enable_button(callback_function)


class qcm:
    def get_qcm_frequency():
        raise NotImplementedError()