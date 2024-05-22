import serial
import serial.tools.list_ports
import time,random

class ArduinoCommunicator:
    def __init__(self, baud_rate=9600, timeout=2, expected_response="THIS_IS_ARDUINO"):
        self.baud_rate = baud_rate
        self.timeout = timeout
        self.expected_response = expected_response
        self.arduino_port = None
        self.serial_connection = None
        self.last_reply_from_arduino_time = 0  # Time of last reply from Arduino
        
    def calculate_time_since_last_reply(self):
        return f"{time.time() - self.last_reply_from_arduino_time:2f} seconds since last reply from Arduino"
    
    def close_serial_connection(self):
        if self.serial_connection is not None and self.serial_connection.isOpen():
            self.serial_connection.close()

        self.serial_connection = None
        self.arduino_port = None
        
    def find_and_connect_to_arduino_if_possible(self)->bool:
        ports = serial.tools.list_ports.comports()
        
        self.close_serial_connection()
        
        for port in ports:
            try:
                ser = serial.Serial(port.device, self.baud_rate, timeout=self.timeout)
                time.sleep(2)  # Wait for Arduino to reset
                ser.write(b'i') # After receiving this character, arduino returns the 'expected_response'
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response == self.expected_response:
                    self.arduino_port = port.device
                    self.serial_connection = ser
                    return True # Connected to Arduino
            except (OSError, serial.SerialException):
                continue # Try next port
        return False # Not connected to Arduino

    def is_connected_to_arduino(self):
        if self.serial_connection is not None and self.serial_connection.isOpen():
            try:
                self.serial_connection.write(b'i')
                response = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                self.last_reply_from_arduino_time = time.time()
                return (response == self.expected_response) # True if response is as expected    
            except (serial.SerialException, UnicodeDecodeError):
                return False
        return False
        
    def send_data(self, data):
        try:
            self.serial_connection.write(data.encode())
        except serial.SerialException:
            print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} (SERIAL EXCEPTION) send_data()\n     -> SerialException occurred while sending data to Arduino")
        
    def receive_data(self)-> str:
        try:
            reply =  self.serial_connection.readline().decode('utf-8', errors='ignore').strip().replace("\n","")
            if reply in ["ECHO_0", "ECHO_1"]:
                self.last_reply_from_arduino_time = time.time()
            return reply
        except serial.SerialException:
            print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} (SERIAL EXCEPTION) receive_data()\n     -> SerialException occurred while receiving data from Arduino")
 
    def check_and_reconnect_if_disconnected(self):
        if not arduino_communicator.is_connected_to_arduino():
            print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} (NOT CONNECTED) check_and_reconnect_if_disconnected()\n     -> Trying to connect to Arduino")
            if arduino_communicator.find_and_connect_to_arduino_if_possible():
                print("     -> Connected to Arduino")
            else:
                print("     -> Arduino not found in ports")       

    def send_activate_turnstile_signal(self):
            try:
                arduino_communicator.send_data("1")
                print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} (ACTIVATE TURNSTILE) send_activate_turnstile_signal()\n     -> Data '1' sent to Arduino") 
            except Exception as e:                
                print(e)

    def send_ping_to_arduino(self):
            try:
                arduino_communicator.send_data("0")
                print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} (PING ARDUINO) send_ping_to_arduino()\n     -> Data '0' sent to Arduino") 
            except Exception as e:
                print(e)
      

if __name__ == "__main__":
    arduino_communicator = ArduinoCommunicator(expected_response="THIS_IS_ARDUINO")

    while True:
        arduino_communicator.check_and_reconnect_if_disconnected()

        
        # print(arduino_communicator.is_connected_to_arduino())
        # arduino_communicator.send_ping_to_arduino()

        time.sleep(1)