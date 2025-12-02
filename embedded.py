#import qcm_data_collection
import time
import collections

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
        for _ in range(self.__FREQUENCY_SAMPLE_SIZE):
            sample_sums += qcm.get_qcm_frequency()
            time.sleep(self.__SECONDS_BETWEEN_SAMPLES)

        self.__stop_pump()

    def clean(self):
        self.__start_pump()
        time.sleep(self.__CLEANING_TIME_SECONDS)
        self.__stop_pump()

    
# sudo apt update
# sudo apt install python3-dev python3-pip python3-setuptools
# pip3 install RPi.GPIO - GPIO can only be installed on a Raspberry Pi OS.
# used to get data from the QCM pin.
class qcm:
    """QCM input helper with simple denoising and frequency estimation.

    Reads a digital input pin (or simulates one if RPi.GPIO isn't available),
    counts rising edges over a short window to estimate frequency (Hz), and
    applies moving-average + exponential moving-average smoothing.
    """

    QCM_PIN = 3
    _gpio_initialized = False
    _use_gpio = True
    QCM_MEASURE_WINDOW = 0.05  # seconds per internal measurement window
    DEBOUNCE_TIME = 0.0005    # ignore changes shorter than this (seconds)
    SMOOTHING_WINDOW = 5
    _ma_buffer = collections.deque(maxlen=SMOOTHING_WINDOW)
    _ema_alpha = 0.3
    _ema = None

    @classmethod
    def _init_gpio(cls):
        try:
            import RPi.GPIO as GPIO
            cls.GPIO = GPIO
            cls.GPIO.setwarnings(False)
            cls.GPIO.setmode(cls.GPIO.BCM)
            cls.GPIO.setup(cls.QCM_PIN, cls.GPIO.IN)
            cls._gpio_initialized = True
            cls._use_gpio = True
        except Exception:
            # Fall back to a simulator when not running on Raspberry Pi
            cls.GPIO = None
            cls._gpio_initialized = True
            cls._use_gpio = False

    @classmethod
    def _read_raw(cls):
        """Return raw digital input from the pin (0 or 1)."""
        if not cls._gpio_initialized:
            cls._init_gpio()
        if cls._use_gpio and cls.GPIO is not None:
            return cls.GPIO.input(cls.QCM_PIN)
        # Simulator: pseudo-square wave for local testing (~10 Hz when polled fast)
        return int((time.time() * 20) % 2)

    @classmethod
    def get_qcm_frequency(cls):
        """Estimate frequency in Hz by counting rising edges.

        Uses a short polling window and debouncing to avoid counting noise,
        then smooths measurements using moving average and EMA.
        """
        end_time = time.time() + cls.QCM_MEASURE_WINDOW
        last = cls._read_raw()
        last_change_time = time.time()
        count = 0

        while time.time() < end_time:
            cur = cls._read_raw()
            if cur != last:
                now = time.time()
                if now - last_change_time >= cls.DEBOUNCE_TIME:
                    # count rising edges only
                    if last == 0 and cur == 1:
                        count += 1
                    last_change_time = now
                    last = cur
            time.sleep(0.0005)

        frequency = count / cls.QCM_MEASURE_WINDOW

        # moving average buffer
        cls._ma_buffer.append(frequency)
        ma = sum(cls._ma_buffer) / len(cls._ma_buffer)

        # exponential moving average
        if cls._ema is None:
            cls._ema = ma
        else:
            cls._ema = cls._ema_alpha * ma + (1 - cls._ema_alpha) * cls._ema

        return cls._ema