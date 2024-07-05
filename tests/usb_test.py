import serial
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
# Try each port to connect to Arduino
print("Available ports:")
for i, port in enumerate(ports):
    print(i, port.device)
           
      