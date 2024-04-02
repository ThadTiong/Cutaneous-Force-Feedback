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


def draw_grid1(screen, array, data):
    font = pygame.font.SysFont(None, 36)
    label_font = pygame.font.SysFont("Arial", 24)  # Define the font for the label
    max_data_value = max(data)
    min_data_value = min(data)
    border_color = (255, 255, 255)  # White border
    border_thickness = 2  # Thickness of the border
    label_text = "Actuator States"  # Label text

    # Render the label text
    label_surface = label_font.render(label_text, True, (255, 255, 255))  # White text
    # Calculate label position (above the grid)
    label_x = game1_origin[0]
    label_y = (
        game1_origin[1] - label_surface.get_height() - 10
    )  # 10 pixels above the grid
    # Blit the label on the screen
    screen.blit(label_surface, (label_x, label_y))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            index = row * GRID_SIZE + col

            # Calculate the position and size for each cell
            cell_x = game1_origin[0] + col * (SQUARE_SIZE + MARGIN)
            cell_y = game1_origin[1] + row * (SQUARE_SIZE + MARGIN)
            cell_size = SQUARE_SIZE

            # Draw the white border rectangle
            pygame.draw.rect(
                screen, border_color, (cell_x, cell_y, cell_size, cell_size)
            )

            if array[index] == 1:
                if max_data_value != min_data_value:
                    normalized_value = int(
                        (data[index] - min_data_value)
                        / (max_data_value - min_data_value)
                        * 255
                    )
                else:
                    normalized_value = 255
                color = (normalized_value, normalized_value, normalized_value)
            else:
                color = BLACK

            # Draw the colored rectangle inside the border
            pygame.draw.rect(
                screen,
                color,
                (
                    cell_x + border_thickness,
                    cell_y + border_thickness,
                    cell_size - border_thickness * 2,
                    cell_size - border_thickness * 2,
                ),
            )

            text_surface = font.render("", True, (255, 0, 0))
            text_rect = text_surface.get_rect(
                center=(
                    cell_x + cell_size // 2,
                    cell_y + cell_size // 2,
                )
            )
            screen.blit(text_surface, text_rect)


def draw_grid2(screen, data):
    new_min = 100  # Minimum brightness level to avoid too dark colors
    new_max = 255  # Maximum brightness level to prevent overly bright colors
    black = (0, 0, 0)  # Define black for easy reference
    border_color = (255, 255, 255)  # White border color
    border_thickness = 2  # Thickness of the border
    label_text = "Sensor Heatmap"  # Label text
    actual_max_data_value = max(data)  # Get the actual maximum data value
    actual_min_data_value = min(
        [x for x in data if x > 0], default=0
    )  # Get the actual minimum non-zero data value

    # Adjust for cases where all non-zero data values are the same
    if actual_min_data_value == actual_max_data_value:
        actual_min_data_value = 0

    # Render the label text
    label_font = pygame.font.SysFont("Arial", 24)  # Define the font for the label
    label_surface = label_font.render(label_text, True, (255, 255, 255))  # White text
    # Calculate label position (above the grid)
    label_x = game2_origin[0]
    label_y = (
        game2_origin[1] - label_surface.get_height() - 10
    )  # 10 pixels above the grid
    # Blit the label on the screen
    screen.blit(label_surface, (label_x, label_y))

    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            data_value = data[row * GRID_SIZE + col]

            # Calculate the position and size for each cell
            cell_x = game2_origin[0] + col * (SQUARE_SIZE + MARGIN)
            cell_y = game2_origin[1] + row * (SQUARE_SIZE + MARGIN)
            cell_size = SQUARE_SIZE

            # Draw the white border rectangle
            pygame.draw.rect(
                screen, border_color, (cell_x, cell_y, cell_size, cell_size)
            )

            if data_value == 0:
                color = black
            else:
                # Normalize data value dynamically based on actual data range
                if actual_max_data_value != actual_min_data_value:
                    scaled_value = int(
                        new_min
                        + (
                            (data_value - actual_min_data_value)
                            / (actual_max_data_value - actual_min_data_value)
                        )
                        * (new_max - new_min)
                    )
                else:
                    # If all data values are the same and non-zero, use maximum brightness
                    scaled_value = new_max
                color = (scaled_value, scaled_value, scaled_value)

            # Draw the colored rectangle inside the border
            pygame.draw.rect(
                screen,
                color,
                (
                    cell_x + border_thickness,
                    cell_y + border_thickness,
                    cell_size - border_thickness * 2,
                    cell_size - border_thickness * 2,
                ),
            )


def get_oscillation_binary(force_values, vibration_start_times, current_time, count):
    binary_list = [1 if x != 0 else 0 for x in force_values]
    max_value = max(force_values)
    value_range = max_value - min(force_values) if max_value != min(force_values) else 1

    summary_dict = {
        "force_values": force_values.copy(),
        "count": count,
        "current_time": current_time,
        "binary_list": binary_list.copy(),
        "vibration_start_times": vibration_start_times.copy(),
        "max_value": max_value,
        "value_range": value_range,
        "details": {},
    }

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

            summary_dict["details"][i] = {
                "force_values_i": force_values[i],
                "difference": difference,
                "dynamic_interval": dynamic_interval,
                "elapsed_time": elapsed_time,
                "isActive": isActive,
            }

        if (
            force_values[i] == max_value and max_value != 0
        ):  # Changed & to and for correctness
            binary_list[i] = 1

    summary_dict["new_binary_list"] = binary_list.copy()
    summary_dict["new_vibration_start_times"] = vibration_start_times.copy()

    return summary_dict, binary_list, vibration_start_times


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


# Loop constants
SEQUENCE_INTERVAL = 4  # Interval for processing data
OSCILLATION_INTERVAL = 1  # Interval in seconds for changing state
summary = []
# Initial Data
binary_list = [0] * 16
force_values = [0] * (GRID_SIZE**2)
vibration_start_times = [time.time()] * 16  # Initialize start times for vibration

# Serial Setup
serial_port = "/dev/tty.usbmodem1301"
serial_output_port = "/dev/tty.usbmodem1401"
baud_rate = 115200
ser = serial.Serial(serial_port, baud_rate)
outputser = serial.Serial(serial_output_port, baud_rate)


# Assuming other parts of your code remain unchanged

try:
    counter = 0
    loop = 0
    count = 1
    running = True
    previous_string = ""

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        current_time = time.time()

        # force_values = [350, 325, 300, 50, 325, 300, 50, 0, 300, 50, 0, 0, 50, 0, 0, 0]
        if ser.in_waiting > 0:
            incoming_data = ser.readline().decode("utf-8").rstrip()
            force_values = [int(x) for x in incoming_data.split(",") if x.strip()]
        counter += 1
        if counter == SEQUENCE_INTERVAL:

            # Pass the properly initialized vibration_start_times instead of an empty list

            new_summary, binary_list, vibration_start_times = get_oscillation_binary(
                force_values,
                vibration_start_times,
                current_time,
                counter,
            )
            # previous_string = print_string(binary_list, "")
            summary.append(new_summary)

            counter = 0
        else:
            summary.append(
                {
                    "force_values": force_values.copy(),
                    "count": counter,
                    "current_time": current_time,
                    "binary_list": binary_list.copy(),
                    "vibration_start_times": vibration_start_times.copy(),
                }
            )
        count += 1
        loop += 1

        if loop == 500:
            save_summary_to_json(
                summary
            )  # Use the new function to save the summary in JSON format
            print("done")

        screen.fill(BLACK)
        draw_grid2(screen, force_values)
        draw_grid1(screen, binary_list, force_values)
        pygame.display.flip()
        time.sleep(0.01)


except Exception as e:
    print(f"An error occurred: {e}")
finally:
    ser.close()
    pygame.quit()
