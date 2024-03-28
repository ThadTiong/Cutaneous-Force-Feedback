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
serial_port = "/dev/tty.usbmodem21201"
# serial_output_port = (
#     "/dev/tty.usbmodem21401"  # Ensure this is the correct path for the output device
# )
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)
# outputser = serial.Serial(
#     serial_output_port, baud_rate
# )  # Output serial port initialization

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

previous_string = ""


def update_boolean_array(data_list, boolean_array, vibration_start_times, current_time):
    max_value = max(data_list)
    # Ensure we don't divide by zero if all values in data_list are the same
    value_range = max_value - min(data_list) if max_value != min(data_list) else 1

    for i in range(len(boolean_array)):
        if boolean_array[i] == 1:  # Only consider initially active (1) indices
            # Calculate dynamic interval based on value difference
            difference = max_value - data_list[i]
            dynamic_interval = (difference / value_range) * (
                vibration_interval * 2
            )  # Adjust the multiplier as needed

            if current_time - vibration_start_times[i] >= dynamic_interval:
                # Toggle the boolean_array value
                boolean_array[i] = 0 if boolean_array[i] == 1 else 1
                vibration_start_times[i] = current_time

        # Ensure the index with the current max value is always 1
        if data_list[i] == max_value & max_value != 0:
            boolean_array[i] = 1


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
            # incoming_data = ser.readline().decode("utf-8").rstrip()
            # data_list = [int(x) for x in incoming_data.split(",") if x.strip()]
            data_list = [350, 325, 300, 50, 325, 300, 50, 0, 300, 50, 0, 0, 50, 0, 0, 0]
            boolean_array = [1 if x != 0 else 0 for x in data_list]
            update_boolean_array(
                data_list, boolean_array, vibration_start_times, current_time
            )

        screen.fill(BLACK)
        # max_index = data_list.index(max(data_list))
        # change_array(boolean_array, data_list[max_index], max_index)

        draw_grid2(screen, data_list)
        # print_string(boolean_array, previous_string)

        draw_grid1(screen, boolean_array)
        pygame.display.flip()
        # rotate display
        time.sleep(0.1)

except serial.SerialException as e:
    print(f"Error opening serial port: {e}")
finally:
    ser.close()
    pygame.quit()
