# -*- coding: utf-8 -*-

import serial
import sqlite3
import time

class frequency_grabber:
    __ser=None
    __conn=None
    __cursor=None
   
    def __init__(self):
        # Set the correct Serial port
        #More robust error handling would be better here, this is for testing
        try:
            self.__ser = serial.Serial('/dev/ttyACM0', 115200, timeout=1)
            print("Successful connection established")
        except Exception as e:
            self.__ser = None
            print("An error occured during setup:",e)

        time.sleep(2)  # wait for Arduino to reset
        if self.__ser: self.__ser.reset_input_buffer()

        # SQLite setup
        self.__conn = sqlite3.connect("qcm_data.db", check_same_thread=False)
        self.__cursor = self.__conn.cursor()
        self.__cursor.execute("""
            CREATE TABLE IF NOT EXISTS qcm_frequency (
                timestamp TEXT,
                frequency REAL
            )
        """)
        self.__conn.commit()

    def getQCMFreq(self):
        try:
            line = self.__ser.readline().decode('utf-8').strip()
            if line.isdigit():
                freq = float(line)
                print(f"Frequency: {freq} Hz")
                
                timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
                self.__cursor.execute("INSERT INTO qcm_frequency (timestamp, frequency) VALUES (?, ?)",
                            (timestamp, freq))
                self.__conn.commit()
                return freq
            else:
                print(line)
            return -1
        except Exception as error:
            print(error)
            return -1
    
    def __del__(self):
        self.__ser.close()
        self.__conn.close()