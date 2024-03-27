import pygame
import sys
import serial
import time

# Initialize pygame
pygame.init()

# Game Setup
GRID_SIZE = 4
SQUARE_SIZE = 100
MARGIN = 50
WINDOW_WIDTH = 1000
WINDOW_HEIGHT = 600

game1_width = GRID_SIZE * (SQUARE_SIZE + MARGIN) + MARGIN * 2
game2_width = WINDOW_HEIGHT  # Use available window height
WINDOW_WIDTH = game1_width + game2_width + MARGIN

# Ensure minimum height (if needed)
WINDOW_HEIGHT = max(WINDOW_HEIGHT, game1_width)

screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Serial Setup
serial_port = "/dev/tty.usbmodem101"
baud_rate = 9600
ser = serial.Serial(serial_port, baud_rate)

# Initial Data
boolean_array = [0] * 16
data_list = [0] * (GRID_SIZE**2)
toggle_times = [time.time()] * len(
    data_list
)  # Track the last toggle time for each element
intervals = [1] * len(data_list)  # Default interval of 1 second for each element

# Game 1 - Grid Editor Positioning
game1_origin = (MARGIN, MARGIN)

# Game 2 - Serial Display Positioning
game2_origin = (game1_origin[0] + GRID_SIZE * (SQUARE_SIZE + MARGIN) + MARGIN, MARGIN)


def draw_grid1(screen, array):
    font = pygame.font.SysFont(None, 36)
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = WHITE if array[row * GRID_SIZE + col] else BLACK
            pygame.draw.rect(
                screen,
                color,
                (
                    game1_origin[0] + col * (SQUARE_SIZE + MARGIN),
                    game1_origin[1] + row * (SQUARE_SIZE + MARGIN),
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )

            index = row * GRID_SIZE + col
            text_surface = font.render(str(index), True, (255, 0, 0))  # Red text
            text_rect = text_surface.get_rect(
                center=(
                    game1_origin[0] + col * (SQUARE_SIZE + MARGIN) + SQUARE_SIZE // 2,
                    game1_origin[1] + row * (SQUARE_SIZE + MARGIN) + SQUARE_SIZE // 2,
                )
            )
            screen.blit(text_surface, text_rect)


def draw_grid2(screen, data):
    square_size = WINDOW_HEIGHT // GRID_SIZE
    for i in range(GRID_SIZE):
        for j in range(GRID_SIZE):
            scaled_value = int((data[i * GRID_SIZE + j] / 1023) * 255)
            color = (scaled_value, scaled_value, scaled_value)
            rect = pygame.Rect(
                game2_origin[0] + j * square_size,
                game2_origin[1] + i * square_size,
                square_size,
                square_size,
            )
            pygame.draw.rect(screen, color, rect)


def update_boolean_array(
    data_list, boolean_array, toggle_times, intervals, current_time
):
    max_value = max(data_list)
    for i in range(len(data_list)):
        distance = abs(data_list[i] - max_value)
        intervals[i] = (
            max(0.1, 1 - distance / max_value) if max_value else 1
        )  # Adjust the interval calculation as needed
        if current_time - toggle_times[i] >= intervals[i]:
            boolean_array[i] = 1 if boolean_array[i] == 0 else 0
            toggle_times[i] = current_time


def calculate_intervals(data_list):
    max_value = max(data_list)
    intervals = []
    for value in data_list:
        # Calculate difference ratio (0 to 1)
        difference_ratio = (max_value - value) / max_value
        # Convert ratio to interval (100ms to 1 second)
        interval = 100 + (900 * difference_ratio)
        intervals.append(interval)
    return intervals


# Initialize last update times for each square
last_update_times = [0] * len(data_list)
# Calculate intervals once outside the loop to start
vibration_intervals = calculate_intervals(data_list)

try:
    running = True
    while running:
        current_time = pygame.time.get_ticks()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Assume you have new data_list values here
        # Update vibration intervals if data_list updated
        # vibration_intervals = calculate_intervals(data_list)

        for i in range(len(boolean_array)):
            # Skip non-vibrating squares
            if boolean_array[i] == 0:
                continue

            # Check if it's time to toggle the state
            if current_time - last_update_times[i] > vibration_intervals[i]:
                # Toggle boolean_array[i]
                boolean_array[i] = 1 - boolean_array[i]
                # Reset last update time
                last_update_times[i] = current_time

        # Your drawing and game logic here...

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
finally:
    ser.close()
    pygame.quit()
