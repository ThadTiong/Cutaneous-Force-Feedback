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
serial_port = "/dev/tty.usbmodem21301"
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)

# Initial Data
boolean_array = [0] * 16
data_list = [0] * (GRID_SIZE**2)
vibration_start_times = [time.time()] * 16  # Initialize start times for vibration
vibration_interval = 0.5  # Interval in seconds for changing state

# Game 1 - Grid Editor Positioning
game1_origin = (MARGIN, MARGIN)

# Game 2 - Serial Display Positioning
game2_origin = (game1_origin[0] + GRID_SIZE * (SQUARE_SIZE + MARGIN) + MARGIN, MARGIN)

# Define the draw functions for both games...


def update_boolean_array(data_list, boolean_array, vibration_start_times, current_time):
    # Determine the index with the maximum value
    max_index = data_list.index(max(data_list))
    # Process each index
    for i in range(len(boolean_array)):
        # If the current index is for the maximum value, ensure it's set to 1
        if i == max_index:
            boolean_array[i] = 1
        # For other indices, proceed only if they were initially set to oscillate
        elif boolean_array[i] in [0, 1]:  # Initially set to oscillate
            if current_time - vibration_start_times[i] >= vibration_interval:
                # Toggle the state for oscillation, only if it was already 1
                if boolean_array[i] == 1:  # Only toggle if initially 1
                    boolean_array[i] = 0
                    vibration_start_times[i] = current_time
                elif vibration_start_times[i] == 0:  # Reset if it was 0
                    boolean_array[i] = 1
                    vibration_start_times[i] = current_time


def print_string(boolean_array):
    first = 0
    second = 0

    values = [1, 8, 1, 8, 2, 16, 2, 16, 4, 32, 4, 32, 64, 128, 64, 128]

    for i in range(len(boolean_array)):

        if i % 4 in {0, 1}:  # Check for indices divisible by 4 or with remainder 1
            if boolean_array[i]:
                first += values[i]
        elif i % 4 in {2, 3}:  # Check for indices divisible by 4 with remainder 2 or 3
            if boolean_array[i]:
                second += values[i]

    print("First:", first)
    print("Second:", second)


def draw_grid1(screen, array):
    font = pygame.font.SysFont(None, 36)  # Choose a suitable font and size
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

            # Render the index text
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
    square_size = WINDOW_HEIGHT // GRID_SIZE  # Scale to fit in the window
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


try:
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time()

        if ser.in_waiting > 0:
            incoming_data = ser.readline().decode("utf-8").rstrip()
            data_list = [int(x) for x in incoming_data.split(",") if x.strip()]
            boolean_array = [1 if x != 0 else 0 for x in data_list]
            update_boolean_array(
                data_list, boolean_array, vibration_start_times, current_time
            )

        screen.fill(BLACK)
        # max_index = data_list.index(max(data_list))
        # change_array(boolean_array, data_list[max_index], max_index)

        draw_grid2(screen, data_list)
        print_string(boolean_array)

        draw_grid1(screen, boolean_array)
        pygame.display.flip()
        time.sleep(0.01)

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
finally:
    ser.close()
    pygame.quit()
