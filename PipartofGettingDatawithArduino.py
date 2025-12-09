#sudo apt-get update
#sudo apt-get install python3-pip
#sudo apt-get install python3-dev
#sudo apt-get install i2c-tools
#pip3 install smbus2 spidev pyserial sqlite3

import serial
import sqlite3
import time

class fequency_grabber:
    ser=None
    conn=None
    cursor=None
   
    def __init__(self):
        # Set the correct Serial port
        self.ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
        time.sleep(2)  # wait for Arduino to reset
        self.ser.reset_input_buffer()

        # SQLite setup
        self.conn = sqlite3.connect("qcm_data.db")
        self.cursor = self.conn.cursor()
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS qcm_frequency (
                timestamp TEXT,
                frequency REAL
            )
        """)
        self.conn.commit()

    def getQCMFreq(self):
        try:
            line = self.ser.readline().decode('utf-8').strip()
            if line.isdigit():
                freq = float(line)
                print(f"Frequency: {freq} Hz")
                
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                self.cursor.execute("INSERT INTO qcm_frequency (timestamp, frequency) VALUES (?, ?)",
                            (timestamp, freq))
                self.conn.commit()
        except Exception as error:
            print(error)
    
    def __del__(self):
        self.ser.close()
        self.conn.close()