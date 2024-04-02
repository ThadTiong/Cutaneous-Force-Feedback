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
game2_width = WINDOW_HEIGHT
WINDOW_WIDTH = game1_width + game2_width + MARGIN
game1_origin = (MARGIN, MARGIN)
game2_origin = (game1_origin[0] + GRID_SIZE * (SQUARE_SIZE + MARGIN) + MARGIN, MARGIN)
WINDOW_HEIGHT = max(WINDOW_HEIGHT, game1_width)
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)


# Initial Data
boolean_array = [0] * 16
data_list = [0] * (GRID_SIZE**2)
vibration_start_times = [time.time()] * 16  # Initialize start times for vibration


# Loop constants
DATA_INTERVAL = 3  # Interval for processing data
VIBRATION_DELAY = 1  # Interval in seconds for changing state


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


def update_boolean_array(data_list, boolean_array, vibration_start_times, current_time):
    max_value = max(data_list)

    value_range = max_value - min(data_list) if max_value != min(data_list) else 1
    print("Current Time: ", current_time)
    print("Boolean Array: ", boolean_array)
    print("Max value: ", max_value)
    print("Value Range: ", value_range)
    print("Virtual Start Times: ", vibration_start_times)

    for i in range(len(boolean_array)):
        if boolean_array[i] == 1:  # Only consider initially active (1) indices
            # Calculate dynamic interval based on value difference
            difference = max_value - data_list[i]
            dynamic_interval = (difference / value_range) * (
                VIBRATION_DELAY
            )  # Adjust the multiplier as needed

            elapsed_time = current_time - vibration_start_times[i]

            print("Data list[i]: ", data_list[i])
            print("Difference: ", difference)
            print("Dynamic Interval: ", dynamic_interval)
            print("Elapsed Time: ", elapsed_time)

            if elapsed_time >= dynamic_interval:
                # Toggle the boolean_array value
                boolean_array[i] = 1 if boolean_array[i] == 0 else 1
                vibration_start_times[i] = current_time

            else:
                boolean_array[i] = 0

        # Ensure the index with the current max value is always 1
        if data_list[i] == max_value & max_value != 0:
            boolean_array[i] = 1
    print("Updated Boolean Array: ", boolean_array)
    print("Updated Virtual Start Times: ", vibration_start_times)


try:
    counter = 0
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time()

        counter += 1
        if counter == DATA_INTERVAL:
            data_list = [350, 325, 300, 50, 325, 300, 50, 0, 300, 50, 0, 0, 50, 0, 0, 0]
            boolean_array = [1 if x != 0 else 0 for x in data_list]
            update_boolean_array(
                data_list, boolean_array, vibration_start_times, current_time
            )
            counter = 0

        screen.fill(BLACK)

        draw_grid2(screen, data_list)

        draw_grid1(screen, boolean_array)
        pygame.display.flip()
        # rotate display
        time.sleep(0.01)

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
finally:
    # ser.close()
    pygame.quit()
