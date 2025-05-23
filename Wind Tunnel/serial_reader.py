import serial
import time

class SerialReader:
    def __init__(self, port, rate):
        """Establishes the connection with the arduino serial."""
        try:
            self.arduino = serial.Serial(port, rate, timeout=1)
        except serial.SerialException as e:
            print(f"Error opening serial port {port}: {e}")
            raise
        time.sleep(2)

    def get_data(self):
        """Receives data from Arduino over serial."""
        if self.arduino.in_waiting > 0:
            line = self.arduino.readline().decode('utf-8').strip()
            if line:
                 data = line.split()
                 return data
        return None
                 
    def close(self):
        """Closes serial port."""
        self.arduino.close()