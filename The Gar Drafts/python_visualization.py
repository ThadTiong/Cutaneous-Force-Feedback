import serial
import pygame
from pygame.locals import *

# Global variables
rect_size = None
max_height = None
serial_in_array = [0] * 16
new_data = False

# Serial setup with reduced timeout for faster response
ser = serial.Serial("/dev/tty.usbmodem101", 115200, timeout=0.05)  # Reduced timeout


def read_serial():
    global new_data
    data = ser.readline().strip().decode("utf-8")
    if data:

        print(data)  # Debug: print incoming serial data
        if data.endswith(","):  # Handle trailing comma
            data = data[:-1]
        values = data.split(", ")
        if len(values) == 16:
            try:
                serial_in_array[:] = [int(val) for val in values]
                new_data = True
            except ValueError as e:
                print("Error converting data to integers:", e)


# Initialize Pygame
pygame.init()
width, height = 600, 600  # Square window
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()  # Used to manage how fast the screen updates


# Function definitions
def setup():
    global rect_size, max_height
    rect_size = width / 4  # Adjusting rectangle size for 2D rendering
    max_height = height


def draw():
    global new_data
    if new_data:
        screen.fill((0, 0, 0))  # Clear the screen before drawing

        for i in range(16):
            x = (i % 4) * rect_size
            y = (i // 4) * rect_size
            rect_height = rect_size  # Each rectangle's height

            # Calculate grayscale color based on input value
            gray_value = int(serial_in_array[i] / 1023 * 255)
            color = (gray_value, gray_value, gray_value)

            pygame.draw.rect(screen, color, (x, y, rect_size, rect_height))

        pygame.display.flip()  # Update the full display Surface to the screen
        new_data = False


def main():
    setup()
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                ser.close()  # Close serial port when quitting
                return

        read_serial()
        draw()
        clock.tick(60)  # Adjusted to 60 FPS for efficiency


if __name__ == "__main__":
    main()
