import serial
import time

# Serial port configuration
serial_output_port = "/dev/tty.usbmodem21401"
baud_rate = 9600  # Adjust as necessary

# Initialize serial connection
ser = serial.Serial(serial_output_port, baud_rate, timeout=1)


# Function to send data to the serial port
def send_data(data):
    ser.write(data.encode())


try:
    while True:
        # Send <000000>
        send_data("<000000>")
        print("Sent: <000000>")
        time.sleep(1)  # Wait for 1 second

        # Send <255255>
        send_data("<255255>")
        print("Sent: <255255>")
        time.sleep(1)  # Wait for 1 second
except KeyboardInterrupt:
    print("Program terminated by user.")

finally:
    ser.close()  # Make sure to close the serial port when done
