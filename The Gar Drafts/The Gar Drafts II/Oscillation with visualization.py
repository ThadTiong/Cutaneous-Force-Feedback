import pygame
import sys
import serial
import time
import csv  # Import CSV module

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
DATA_INTERVAL = 4  # Interval for processing data
VIBRATION_DELAY = 1  # Interval in seconds for changing state

# Initialize a list to hold data for CSV output
csv_data = []
loop_counter = 0  # Track the number of loops


def update_boolean_array(data_list, boolean_array, vibration_start_times, current_time):
    max_value = max(data_list)
    value_range = max_value - min(data_list) if max_value != min(data_list) else 1

    # Copy the current state before updating
    pre_boolean_array = boolean_array[:]
    pre_vibration_start_times = vibration_start_times[:]

    capture_details = []  # To capture details for each boolean_array element
    for i in range(len(boolean_array)):
        elapsed_time = current_time - vibration_start_times[i]
        is_changed = False  # Flag to check if this index was changed by the algorithm
        if boolean_array[i] == 1:  # Only consider initially active (1) indices
            difference = max_value - data_list[i]
            dynamic_interval = (difference / value_range) * (VIBRATION_DELAY)
            if elapsed_time >= dynamic_interval:
                boolean_array[i] = 0
                vibration_start_times[i] = current_time
                is_changed = True
        else:
            difference = 0
            dynamic_interval = 0

        if data_list[i] == max_value and max_value != 0:
            if boolean_array[i] != 1:  # Check if this change is necessary
                is_changed = True
            boolean_array[i] = 1

        # Capture details including pre and post update information
        capture_details.append((difference, dynamic_interval, elapsed_time, is_changed))

    # Return details along with pre-update and post-update states
    return (
        capture_details,
        pre_boolean_array,
        pre_vibration_start_times,
        boolean_array,
        vibration_start_times,
    )


def save_to_csv(csv_data):
    with open("game_data.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(
            [
                "Current Time",
                "Boolean Array (Before)",
                "Vibration Start Times (Before)",
                "Difference (Each Index)",
                "Dynamic Intervals (Each Index)",
                "Elapsed Times (Each Index)",
                "Is Changed By Algo (Each Index)",
                "Boolean Array (After)",
                "Vibration Start Times (After)",
            ]
        )
        for row in csv_data:
            writer.writerow(row)


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
    data_counter = 0
    while running:
        # Simulated loop - replace with actual game loop and serial port reading
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        data_counter += 1

        if data_counter == DATA_INTERVAL:
            data_list = [
                350,
                325,
                300,
                50,
                325,
                300,
                50,
                0,
                300,
                50,
                0,
                0,
                50,
                0,
                0,
                0,
            ]
            current_time = time.time()
            boolean_array_before = boolean_array[:]
            vibration_start_times_before = vibration_start_times[:]
            (
                capture_details,
                pre_boolean_array,
                pre_vibration_start_times,
                boolean_array,
                vibration_start_times,
            ) = update_boolean_array(
                data_list, boolean_array, vibration_start_times, current_time
            )

            # Process captured details for each index to format them properly for the CSV
            for i, details in enumerate(capture_details):
                row = [
                    current_time,
                    pre_boolean_array,
                    pre_vibration_start_times,
                    details[0],  # Difference
                    details[1],  # Dynamic Interval
                    details[2],  # Elapsed Time
                    details[3],  # Is Changed
                    boolean_array,
                    vibration_start_times,
                ]
                csv_data.append(row)

            loop_counter += 1
            if loop_counter >= 20:
                save_to_csv(csv_data)
                running = False  # Stop the game after saving data for 5 loops

            data_counter = 0

        screen.fill(BLACK)
        draw_grid2(screen, data_list)
        draw_grid1(screen, boolean_array)
        pygame.display.flip()
        time.sleep(0.01)

except Exception as e:
    print(f"Error: {e}")
finally:
    pygame.quit()
