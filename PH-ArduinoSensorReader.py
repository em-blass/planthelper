import serial
import time

# Set up the serial connection (adjust /dev/ttyACM0 to Arduino's port)
ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1)
ser.flush()

while True:
    if ser.in_waiting > 0:
        line = ser.readline().decode('utf-8').rstrip()
        print(line)
        # Add logic here to process and send the data to where it needs to go
        # For example, saving to a file, sending to a database, etc.
    time.sleep(2)  # Adjust the delay as needed