import serial
import threading
import pygame
import sys

# Serial setup
ser_input = serial.Serial('COM10', 115200, timeout=1)
ser_output = serial.Serial('COM12', 115200, timeout=1)

# Pygame setup
pygame.init()
WINDOW_WIDTH = 400
WINDOW_HEIGHT = 400
CELL_SIZE = 50
GRID_WIDTH = 4
GRID_HEIGHT = 4
GRID_TOTAL_WIDTH = CELL_SIZE * GRID_WIDTH
GRID_TOTAL_HEIGHT = CELL_SIZE * GRID_HEIGHT
screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
clock = pygame.time.Clock()

# Global variable to store node values
node_values = [[0] * GRID_WIDTH for _ in range(GRID_HEIGHT)]
thread_lock = threading.Lock()

# Function for reading serial data and updating node values
def read_and_assign_variables():
    global node_values
    while True:
        data = ser_input.readline().strip().decode("utf-8")
        #print(data)
        if data:
            # Remove trailing comma if present
            if data.endswith(','):
                data = data[:-1]
            values = data.split(", ")
            if len(values) == 16:
                try:
                    with thread_lock:
                        # Update node values
                        node_values = [[int(val) for val in values[i:i+4]] for i in range(0, 16, 4)]
                        # Rotate grid by 90 degrees
                        node_values = [list(row) for row in zip(*node_values[::-1])]
                    threads = []
                    for i in range(GRID_HEIGHT):
                        for j in range(GRID_WIDTH):
                            t = threading.Thread(target=process_value, args=(i, j, node_values[i][j]))
                            t.start()
                            threads.append(t)
                    for t in threads:
                        t.join()
                except ValueError as e:
                    print("Error converting data to integers:", e)

# Function to process value for a specific cell
#previousMsg = ""
def process_value(i, j, value):
    if value < 80:
        node_values[i][j] = 0 
    elif value > 255:
        node_values[i][j] = 255

    cell_0 = 0
    cell_1 = 0

    if node_values[i][j] >= 150:
        if i == 1 and j == 1: cell_1 += 128
        if i == 1 and j == 2: cell_1 += 32
        if i == 1 and j == 3: cell_1 += 16
        if i == 1 and j == 4: cell_1 += 8
        if i == 2 and j == 1: cell_1 += 64
        if i == 2 and j == 2: cell_1 += 4
        if i == 2 and j == 3: cell_1 += 2
        if i == 2 and j == 4: cell_1 += 1
        if i == 3 and j == 1: cell_0 += 128
        if i == 3 and j == 2: cell_0 += 32
        if i == 3 and j == 3: cell_0 += 16
        if i == 3 and j == 4: cell_0 += 8
        if i == 4 and j == 1: cell_0 += 64
        if i == 4 and j == 2: cell_0 += 4
        if i == 4 and j == 3: cell_0 += 2
        if i == 4 and j == 4: cell_0 += 1

    cell_0_padded = "{:03d}".format(cell_0)
    cell_1_padded = "{:03d}".format(cell_1)
    msg = "<" + cell_0_padded + cell_1_padded + ">"

    #ser_output.write(msg.encode())
    print(msg)

    # if msg != previousMsg:
    #     ser_output.write(msg.encode())
    #     previousMsg = msg


# Function to draw grid
def draw_grid():
    global node_values
    grid_x = (WINDOW_WIDTH - GRID_TOTAL_WIDTH) // 2
    grid_y = (WINDOW_HEIGHT - GRID_TOTAL_HEIGHT) // 2
    for i in range(GRID_HEIGHT):
        for j in range(GRID_WIDTH):
            rect = pygame.Rect(grid_x + j * CELL_SIZE, grid_y + i * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            gray_value = 255 - node_values[i][j] * 255 // 255  # Convert to grayscale (higher values -> lighter)
            color = (gray_value, gray_value, gray_value)
            pygame.draw.rect(screen, color, rect)
            pygame.draw.rect(screen, (0, 0, 0), rect, 1)  # Draw cell borders

# Function to handle events
def handle_events():
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()  # Exit using sys.exit() instead of exit()

def main():
    # Start the thread for reading and assigning variables
    threading.Thread(target=read_and_assign_variables, daemon=True).start()

    # Main loop
    running = True
    while running:
        screen.fill((0, 0, 0))
        draw_grid()
        handle_events()
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()
