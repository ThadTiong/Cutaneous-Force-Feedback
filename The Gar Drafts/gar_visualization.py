from os import write
import sys
import pygame
import serial
import time

# Pygame setup
pygame.init()
window_size = (400, 400)
screen = pygame.display.set_mode(window_size)
pygame.display.set_caption("Serial Input Display")

# Colors
black = (0, 0, 0)
white = (255, 255, 255)

# Grid setup
grid_size = 4  # 4x4 grid
square_size = window_size[0] // grid_size  # Size of squares

# Serial setup
serial_port = "/dev/tty.usbmodem21301"
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate)
print(f"Connected to {serial_port} at {baud_rate} baud.")
prev_data = [0] * grid_size**2


def draw_grid(data):
    for i in range(grid_size):
        for j in range(grid_size):
            # Scale the input value to the range 0-255 (for RGB values)
            scaled_value = int((data[i * grid_size + j] / 1023) * 255)
            # Ensure that the value is within the bounds of 0-255
            scaled_value = max(0, min(255, scaled_value))
            # Use the scaled value for the RGB components to create a shade of gray
            color = (scaled_value, scaled_value, scaled_value)
            # Determine the position and size of each square
            rect = pygame.Rect(
                j * square_size, i * square_size, square_size, square_size
            )
            pygame.draw.rect(screen, color, rect)


try:
    running = True
    while running:
        # Check for Pygame quit event
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Read data from the serial port
        if ser.in_waiting > 0:
            incoming_data = ser.readline().decode("utf-8").rstrip()

            # Convert the incoming data to a list of integers
            # Modified line with filtering to remove any empty strings:
            data_list = [int(x) for x in incoming_data.split(",") if x.strip()]
            processed_list = [1 if x != 0 else 0 for x in data_list]
            # processed list to string
            processed_list_str = "".join(str(x) for x in processed_list)
            sys.stdout.write(processed_list_str + "\n")
            sys.stdout.flush()
            # Draw the grid based on the data
            screen.fill(black)  # Clear screen with black before drawing
            draw_grid(data_list)
            pygame.display.flip()  # Update the display

        time.sleep(0.01)  # Small delay to prevent excessive CPU usage

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
except KeyboardInterrupt:
    print("Program terminated by user.")
finally:
    ser.close()
    print("Serial connection closed.")
    pygame.quit()
