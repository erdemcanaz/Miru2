import serial
import serial.tools.list_ports
import time

class ArduinoCommunicator:
    def __init__(self, baud_rate=9600, timeout=2, expected_response="THIS_IS_ARDUINO"):
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.expected_response = expected_response
        self.serial_connection = None
        self.arduino_port = None

    def find_arduino(self):
        ports = serial.tools.list_ports.comports()
        for port in ports:
            try:
                ser = serial.Serial(port.device, self.baud_rate, timeout=self.timeout)
                time.sleep(2)  # Wait for Arduino to reset
                ser.write(b'i')
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response == self.expected_response:
                    self.arduino_port = port.device
                    ser.close()
                    return port.device
                ser.close()
            except (OSError, serial.SerialException):
                continue
        return None

    def connect(self):
        if not self.arduino_port:
            self.arduino_port = self.find_arduino()
        
        if self.arduino_port:
            self.serial_connection = serial.Serial(self.arduino_port, self.baud_rate, timeout=self.timeout)
            time.sleep(2)  # Wait for Arduino to reset
            return True
        else:
            raise Exception("Arduino not found")

    def is_connected(self):
        if self.serial_connection:
            return self.serial_connection.isOpen()
        return False

    def send_data(self, data):
        if self.is_connected():
            self.serial_connection.write(data.encode())
        else:
            raise Exception("Not connected to Arduino")

    def receive_data(self):
        if self.is_connected():
            return self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
        else:
            raise Exception("Not connected to Arduino")

    def close_connection(self):
        if self.is_connected():
            self.serial_connection.close()
        self.serial_connection = None
        self.arduino_port = None

# Example usage
if __name__ == "__main__":
    arduino_communicator = ArduinoCommunicator(expected_response="THIS_IS_ARDUINO")

    while True:
        if arduino_communicator.is_connected():            
            try:
                print("Connecting to Arduino")
                if arduino_communicator.connect():
                    arduino_communicator.send_data('i')
                    response = arduino_communicator.receive_data()
                    print(f"Received: {response}")
            except Exception as e:
                print(e)
            
        print("Connected to Arduino")
        time.sleep(1)
