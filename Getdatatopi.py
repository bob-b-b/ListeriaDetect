#sudo apt-get update
#sudo apt-get install python3-pip
#sudo apt-get install python3-dev
#sudo apt-get install i2c-tools
#pip3 install smbus2 spidev pyserial sqlite3

import time
import sqlite3
import RPi.GPIO as GPIO

# GPIO pin connected to SN74LVC1GX04 output
Driver_pin = 21   # BCM numbering (physical pin 40 <-- will change)

class Frequencygrab: 
    def __init__(self, pin):
        self.pin = pin
        self.count = 0

        # Setup GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

        # Count rising edges from the QCM oscillator output
        GPIO.add_event_detect(self.pin, GPIO.RISING, callback=self.edge_callback)

    def edge_callback(self, channel):
        self.count += 1

    def measure_frequency(self, duration=1.0):
        """Counts rising edges over a measurement window."""
        time.sleep(duration)
        freq=self.count / duration
        self.count = 0
        return freq
    #take note here


    def close(self):
        GPIO.cleanup(self.pin)


class DataLogger:
    def __init__(self, db_name="qcm_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS qcm_frequency (
                timestamp TEXT,
                frequency REAL
            )
        """)
        self.conn.commit()

    def insert_frequency(self, freq):
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute(
            "INSERT INTO qcm_frequency (timestamp, frequency) VALUES (?, ?)",
            (timestamp, freq)
        )
        self.conn.commit()

    def fetch_all(self):
        """Fetch all data from the table."""
        self.cursor.execute("SELECT * FROM qcm_frequency")
        return self.cursor.fetchall()

    def close(self):
        self.conn.close()


def main():
    grabthatfrequency = Frequencygrab(Driver_pin)
    datalogged = DataLogger()
   
    try:
        while True:
            freq = grabthatfrequency.measure_frequency(duration=1.0)
            print(f"Measured Frequency: {freq:.2f} Hz")
            datalogged.insert_frequency(freq)

    except KeyboardInterrupt:
        print("Stopping...")

    finally:
        grabthatfrequency.close()
        datalogged.close()


if __name__ == "__main__":
    main()