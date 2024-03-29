import pygame
import json  # Make sure to import the json module
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


def get_oscillation_binary(
    force_values, binary_list, vibration_start_times, current_time
):
    max_value = max(force_values)
    value_range = max_value - min(force_values) if max_value != min(force_values) else 1

    for i in range(len(binary_list)):
        if binary_list[i] == 1:  # Only consider initially active (1) indices
            difference = max_value - force_values[i]
            dynamic_interval = difference / value_range * OSCILLATION_INTERVAL

            elapsed_time = current_time - vibration_start_times[i]

            if elapsed_time >= dynamic_interval:
                binary_list[i] = 1
                vibration_start_times[i] = current_time
                isActive = "yes"
            else:
                binary_list[i] = 0
                isActive = "no"

        if (
            force_values[i] == max_value and max_value != 0
        ):  # Changed & to and for correctness
            binary_list[i] = 1

    return binary_list


def save_summary_to_json(summary):
    # Assuming summary is a list of dictionaries
    with open("summary.json", "w") as file:
        json.dump(summary, file, indent=4)


def print_string(boolean_array, previous_string):
    first = 0
    second = 0

    values = [1, 8, 1, 8, 2, 16, 2, 16, 4, 32, 4, 32, 64, 128, 64, 128]

    for i in range(len(boolean_array)):
        if i % 4 in {0, 1}:
            if boolean_array[i]:
                first += values[i]
        elif i % 4 in {2, 3}:
            if boolean_array[i]:
                second += values[i]
    full_string = f"<{first:03}{second:03}>"

    # if full_string same as previous string:
    if full_string != previous_string:

        # Write full_string to output serial port
        print(full_string)
        outputser.write(
            full_string.encode("utf-8")
        )  # Ensure to encode the string before sending
        previous_string = full_string
    return previous_string


# Serial Setup
# serial_port = "/dev/tty.usbmodem21301"
# serial_output_port = "/dev/tty.usbmodem21401"
# baud_rate = 115200
# ser = serial.Serial(serial_port, baud_rate)
# outputser = serial.Serial(serial_output_port, baud_rate)


# Loop constants
SEQUENCE_INTERVAL = 4  # Interval for processing data
OSCILLATION_INTERVAL = 1  # Interval in seconds for changing state
summary = []
# Initial Data
binary_list = [0] * 16
force_values = [0] * (GRID_SIZE**2)
vibration_start_times = [time.time()] * 16  # Initialize start times for vibration


# Assuming other parts of your code remain unchanged

try:
    counter = 0
    loop = 0
    previous_string = ""
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time()

        force_values = [350, 325, 300, 50, 325, 300, 50, 0, 300, 50, 0, 0, 50, 0, 0, 0]
        counter += 1
        if counter == SEQUENCE_INTERVAL:

            binary_list = [1 if x != 0 else 0 for x in force_values]
            # Pass the properly initialized vibration_start_times instead of an empty list
            binary_list = get_oscillation_binary(
                force_values, binary_list, vibration_start_times, current_time
            )
            # previous_string = print_string(binary_list, "")
            counter = 0

        screen.fill(BLACK)
        draw_grid2(screen, force_values)
        draw_grid1(screen, binary_list)
        pygame.display.flip()
        time.sleep(0.01)


except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
finally:
    # ser.close()
    pygame.quit()
