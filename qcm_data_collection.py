#sudo apt-get update
#sudo apt-get install python3-pip
#sudo apt-get install python3-dev
#sudo apt-get install i2c-tools
#pip3 install smbus2 spidev pyserial sqlite3

# bash commands we'll most likely need to run on the raspberrypi to get all the dependencies and tools

# cobbling this together from models & tutorials

import time
import serial
import spidev
import smbus2

class PCBDriver:
    def __init__(self, driver_type, port, baudrate=None):
        self.driver_type = driver_type
        self.port = port
        self.baudrate = baudrate 
        #Baudrate is the number of signal changes per second in a communication channel, measured in symbols per second
        # Not sure if that's how we'll do it. This section in general will probably need significant edits since I'm not sure
        # what types of drivers we'll use and what ports they'll be connected to

        # Initialize communication interface
        if self.driver_type == 'UART':
            self.serial_conn = serial.Serial(self.port, self.baudrate)
        elif self.driver_type == 'SPI':
            self.spi_conn = spidev.SpiDev()
            self.spi_conn.open(0, self.port)  # SPI Bus 0, Port
        elif self.driver_type == 'I2C':
            self.i2c_conn = smbus2.SMBus(self.port)
        else:
            raise ValueError("Unsupported driver type")

    def read_data(self):
        """Method to read data from the driver, depends on type."""
        if self.driver_type == 'UART':
            return self.serial_conn.readline()
        elif self.driver_type == 'SPI':
            return self.spi_conn.xfer2([0x00])  # Example read
        elif self.driver_type == 'I2C':
            return self.i2c_conn.read_byte_data(0x68, 0x00)  # Example read from I2C address 0x68
        else:
            raise ValueError("Unsupported driver type")
    
    def close(self):
        """Close the driver connection."""
        if self.driver_type == 'UART':
            self.serial_conn.close()
        elif self.driver_type == 'SPI':
            self.spi_conn.close()
        elif self.driver_type == 'I2C':
            pass  # I2C doesn't need explicit close


# qcm data collection, assumes we're using I2C for it
class QCM:
    def __init__(self, address=0x68, bus=1):
        self.address = address
        self.bus = smbus2.SMBus(bus)  # I2C bus 1
        
    def read_sensor_data(self):
        """Read QCM data via I2C."""
        try:
            data = self.bus.read_i2c_block_data(self.address, 0x00, 8)  # Adjust register address
            # Convert data to usable format (e.g., float, int, etc.)
            return data
        except Exception as e:
            print(f"Error reading QCM data: {e}")
            return None

    def close(self):
        self.bus.close()


# data logging, we can use a simple sqlite database or go even simpler and just export to csv file which might be too simple imo

import sqlite3

class DataLogger:
    def __init__(self, db_name="qcm_data.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
    
    def create_table(self):
        """Create a table to store QCM data."""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS qcm_data (
                timestamp TEXT,
                sensor_data TEXT
            )
        """)
        self.conn.commit()
    
    def insert_data(self, data):
        """Insert new data into the database."""
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        self.cursor.execute("INSERT INTO qcm_data (timestamp, sensor_data) VALUES (?, ?)", (timestamp, str(data)))
        self.conn.commit()
    
    def fetch_all(self):
        """Fetch all data from the table."""
        self.cursor.execute("SELECT * FROM qcm_data")
        return self.cursor.fetchall()

    def close(self):
        """Close the database connection."""
        self.conn.close()


def main():
    # Initialize PCB driver and QCM sensor
    pcb_driver = PCBDriver(driver_type='I2C', port=1)  # Change to match our configuration
    qcm = QCM(address=0x68)
    
    # Initialize the data logger
    logger = DataLogger()
    
    try:
        while True:
            # Read data from the PCB driver
            pcb_data = pcb_driver.read_data()
            print(f"PCB Data: {pcb_data}")
            
            # Read data from the QCM
            qcm_data = qcm.read_sensor_data()
            if qcm_data:
                print(f"QCM Data: {qcm_data}")
                logger.insert_data(qcm_data)
            
            time.sleep(1)  # Adjust the delay as needed

    except KeyboardInterrupt:
        print("Data collection stopped.")
    finally:
        pcb_driver.close()
        qcm.close()
        logger.close()

if __name__ == "__main__":
    main()


# ran via bash command - python3 qcm_data_collection.py