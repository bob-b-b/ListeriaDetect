# -*- coding: utf-8 -*-
import time
import RPi.GPIO as GPIO
import frequency_grabber

class control:
    PUMP_PWM_GPIO=16
    PUMP_FORWARD_GPIO=20
    PUMP_BACKWARD_GPIO=21
    BUTTON_GPIO=26

    __QCM_FREQUENCY_SAMPLE_SIZE=4
    __SECONDS_BETWEEN_SAMPLES=2

    __CLEANING_TIME_SECONDS=10

    __PWM_DUTY_CYCLE=50
    __PWM_FREQUENCY=255

    __pump_pwm=None

    qcm_interaction=None

    
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

    def __drain_callback(self,button):
        print("Draining callback queue while the process is running {button}")

    def __enable_button(self, callback_function):
        GPIO.add_event_detect(
            self.BUTTON_GPIO,
            GPIO.FALLING,
            callback=callback_function,
            bouncetime=200
        )

    def drain_and_enable_button(self, callback_function):
        GPIO.add_event_detect(
            self.BUTTON_GPIO,
            GPIO.FALLING, 
            callback=self.__drain_callback,
            bouncetime=200
        )
        time.sleep(0.5)
        GPIO.remove_event_detect(self.BUTTON_GPIO)
        self.__enable_button(callback_function)

    def disable_button(self):
        GPIO.remove_event_detect(self.BUTTON_GPIO)
    
    def measure_frequency(self):
        self.__start_pump()

        sample_sums=0
        for _ in range(self.__QCM_FREQUENCY_SAMPLE_SIZE):
            sample_sums+=self.qcm_interaction.getQCMFreq()
            time.sleep(self.__SECONDS_BETWEEN_SAMPLES)
            print("Frequency current frequency sum:", sample_sums)

        self.__stop_pump()
        
        return sample_sums/self.__QCM_FREQUENCY_SAMPLE_SIZE

    def clean(self):
        self.__start_pump(reverse=True)
        time.sleep(self.__CLEANING_TIME_SECONDS)
        self.__stop_pump()

    def __init__(self, callback_function):
        GPIO.setmode(GPIO.BCM)
        
        GPIO.setup(self.PUMP_PWM_GPIO, GPIO.OUT)
        self.__pump_pwm=GPIO.PWM(self.PUMP_PWM_GPIO, self.__PWM_FREQUENCY)

        GPIO.setup(self.PUMP_FORWARD_GPIO, GPIO.OUT)
        GPIO.setup(self.PUMP_BACKWARD_GPIO, GPIO.OUT)

        GPIO.setup(self.BUTTON_GPIO, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.__enable_button(callback_function)

        self.qcm_interaction=frequency_grabber.frequency_grabber()

    def __del__(self):
        del self.qcm_interaction
        self.__pump_pwm.stop()
        GPIO.cleanup()
