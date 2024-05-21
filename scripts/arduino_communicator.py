import serial
import serial.tools.list_ports
import time

class ArduinoCommunicator:
    def __init__(self, baud_rate=9600, timeout=2, expected_response="THIS_IS_ARDUINO"):
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.expected_response = expected_response
        self.arduino_port = None
        self.serial_connection = None
        self.last_reply_from_arduino_time = 0  # Time of last reply from Arduino

    def find_and_connect_to_arduino_if_possible(self)->bool:
        ports = serial.tools.list_ports.comports()

        if self.serial_connection is not None and self.serial_connection.isOpen():
            self.serial_connection.close()

        self.serial_connection = None
        self.arduino_port = None

        for port in ports:
            try:
                ser = serial.Serial(port.device, self.baud_rate, timeout=self.timeout)
                time.sleep(2)  # Wait for Arduino to reset
                ser.write(b'i') # After receiving this character, arduino returns the 'expected_response'
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response == self.expected_response:
                    self.arduino_port = port.device
                    self.serial_connection = ser
                    return True
                ser.close()
            except (OSError, serial.SerialException):
                continue
        return False
    
    def is_connected(self):
        if time.time()-self.last_reply_from_arduino_time < 10:
            return True
        else:
            if self.serial_connection and self.serial_connection.isOpen():
                try:
                    self.serial_connection.write(b'i')
                    response = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                    self.last_reply_from_arduino_time = time.time()
                    return (response == self.expected_response) # True if response is as expected    
                except (serial.SerialException, UnicodeDecodeError):
                    return False
            return False

if __name__ == "__main__":
    arduino_communicator = ArduinoCommunicator(expected_response="THIS_IS_ARDUINO")

    while True:
        print(arduino_communicator.is_connected())

        if not arduino_communicator.is_connected():
            print("Trying to connect to Arduino")
            if arduino_communicator.find_and_connect_to_arduino_if_possible():
                print("Connected to Arduino")
            else:
                print("Arduino not found")
        time.sleep(1)
