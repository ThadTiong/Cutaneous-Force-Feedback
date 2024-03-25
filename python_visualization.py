import serial
import pygame
from pygame.locals import *

# Global variables
rect_size = None
max_height = None
serial_in_array = [0] * 16
new_data = False

# Serial setup
ser = serial.Serial('COM17', 115200, timeout=1)

# Initialize Pygame
pygame.init()
width, height = 600, 600  # Adjusted window height to match width for square window
screen = pygame.display.set_mode((width, height))
clock = pygame.time.Clock()

def setup():
    global rect_size, max_height
    rect_size = width / 4  # Adjusting the size of rectangles for 2D rendering
    max_height = height

def draw():
    global new_data
    if new_data:
        screen.fill((0, 0, 0))  # Clear the screen

        for i in range(16):
            x = (i % 4) * rect_size
            y = (i // 4) * rect_size
            rect_height = rect_size

            # Calculate grayscale color based on height
            gray_value = int(serial_in_array[i] / 1023 * 255)
            color = (gray_value, gray_value, gray_value)

            pygame.draw.rect(screen, color, (x, y, rect_size, rect_height))

        # Rotate the surface by 90 degrees counterclockwise
        rotated_surface = pygame.transform.rotate(screen, -90)
        # Flip the rotated surface vertically
        flipped_surface = pygame.transform.flip(rotated_surface, False, True)
        flipped_rect = flipped_surface.get_rect()
        flipped_rect.center = (width / 2, height / 2)

        screen.blit(flipped_surface, flipped_rect)

        pygame.display.flip()
        new_data = False

def read_serial():
    global new_data
    data = ser.readline().strip().decode("utf-8")
    if data:
        # Remove trailing comma if present
        print( data)
        if data.endswith(','):
            data = data[:-1]
        values = data.split(", ")
        if len(values) == 16:
            try:
                serial_in_array[:] = [int(val) for val in values]
                new_data = True
            except ValueError as e:
                print("Error converting data to integers:", e)


def main():
    setup()
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return
        read_serial()
        draw()
        clock.tick(1000)

if __name__ == "__main__":
    main()
