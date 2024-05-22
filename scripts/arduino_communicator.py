import serial
import serial.tools.list_ports
import time,random

class ArduinoCommunicator:
    def __init__(self, baud_rate=9600, serial_timeout=2, expected_response="THIS_IS_ARDUINO", connection_test_period_s = 30, verbose = False, write_delay_s = 0.05):
        self.SERIAL_BAUDRATE = baud_rate
        self.SERIAL_TIMEOUT = serial_timeout
        self.arduino_port = None
        self.serial_connection = None
        self.EXPECTED_RESPONSE = expected_response # When sending 'i' to Arduino, it should reply with this string
        self.WRITE_DELAY_S = write_delay_s

        self.CONNECTION_TEST_PREIOD_S = connection_test_period_s  # Connection timeout in seconds
        self.last_connection_check_time = 0  # Time of last connection check       

        self.VERBOSE = verbose 
        
    def is_connection_test_time_elapsed(self)->bool:
        time_elapsed = time.time() - self.last_connection_check_time
        if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} -> Time elapsed since last connection check: {time_elapsed:.2f} seconds")
        
        return time_elapsed > self.CONNECTION_TEST_PREIOD_S # True if time elapsed is greater than connection test period

    def is_getting_expected_reply_from_port(self)->bool:
        self.last_connection_check_time = time.time() # Update last connection check time

        if self.serial_connection is not None and self.serial_connection.isOpen():
            try:
                self.serial_connection.write(b'i')
                response = self.serial_connection.readline().decode('utf-8', errors='ignore').strip()
                if(response == self.EXPECTED_RESPONSE):
                    if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} -> Expected reply is received, Arduino is online")
                    return True
                else:
                    if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} -> No reply is received, Arduino is offline")

            except (serial.SerialException, UnicodeDecodeError):
                return False
        return False
    
    def find_and_connect_to_arduino_port_if_possible(self)->int:        
        ports = serial.tools.list_ports.comports()
        
        # Close existing serial connection if any
        if self.serial_connection is not None and self.serial_connection.isOpen():
            self.serial_connection.close()

        self.serial_connection = None
        self.arduino_port = None
        
        # Try each port to connect to Arduino
        for port in ports:
            try:
                ser = serial.Serial(port.device, self.SERIAL_BAUDRATE, timeout=self.SERIAL_TIMEOUT)
                time.sleep(2)  # Wait for Arduino to reset
                ser.write(b'i') # After receiving this character, arduino returns the 'expected_response'
                response = ser.readline().decode('utf-8', errors='ignore').strip()
                if response == self.EXPECTED_RESPONSE:
                    self.arduino_port = port.device
                    self.serial_connection = ser
                    if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} -> Connected to Arduino at port {self.arduino_port}")
                    return True # Connected to Arduino
            except (OSError, serial.SerialException):
                if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} -> (EXCEPT) Failed to connect to port {port.device}")
                continue # Try next port
        
        if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} -> Among '{len(ports)}' number of ports, Arduino is not found")
        return False # Not connected to Arduino

    def get_connection_status(self)->bool:
        if self.serial_connection is not None and self.serial_connection.isOpen():
            if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} -> Connection status: {True}")
            return True
        else:
            if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))} -> Connection status: {False}")
            return False

    def ensure_connection(self):
        if self.is_connection_test_time_elapsed():
            if not self.is_getting_expected_reply_from_port():                
                self.find_and_connect_to_arduino_port_if_possible()

    def send_activate_turnstile_signal(self):
        try:
            self.serial_connection.write(b"1")
            if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))}      (ACTIVATE TURNSTILE) -> Data '1' sent to Arduino") 
            time.sleep(self.WRITE_DELAY_S)
        except Exception as e:                
            if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))}      (ACTIVATE TURNSTILE EXCEPT) ->{e}")

    def send_ping_to_arduino(self):
        # Send '0' to Arduino to let arduino know that the connection is still alive
        try:
            self.serial_connection.write(b"0")
            if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))}      (PING ARDUINO) -> Data '0' sent to Arduino") 
            time.sleep(self.WRITE_DELAY_S)
        except Exception as e:                
            if(self.VERBOSE):print(f"{time.strftime('%H:%M:%S', time.gmtime(time.time()))}      (PING ARDUINO EXCEPT) ->{e}")

if __name__ == "__main__":
    arduino_communicator = ArduinoCommunicator(baud_rate=9600, serial_timeout=2, expected_response="THIS_IS_ARDUINO", connection_test_period_s = 10, verbose = True, write_delay_s=0.05)

    while True:
        arduino_communicator.ensure_connection()             
        arduino_communicator.get_connection_status()

        if random.uniform(0,1) < 0.1:
            arduino_communicator.send_activate_turnstile_signal()
        else:
            arduino_communicator.send_ping_to_arduino()
    
        time.sleep(1)
