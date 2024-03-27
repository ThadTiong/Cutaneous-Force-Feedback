import pygame
import sys

# Initialize pygame
pygame.init()

# Constants
WIDTH, HEIGHT = 800, 600
GRID_SIZE = 4
SQUARE_SIZE = 100
MARGIN = 50
ARRAY_FONT_SIZE = 20
GRID_ORIGIN = (
    WIDTH // 2 - (GRID_SIZE * (SQUARE_SIZE + MARGIN)) // 2,
    HEIGHT // 2 - (GRID_SIZE * (SQUARE_SIZE + MARGIN)) // 2,
)
ARRAY_ORIGIN = (50, 50)

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (200, 200, 200)

# Screen setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("4x4 Grid Editor")

# Boolean array for the grid
boolean_array = [0] * 16


# Function to draw the grid based on the boolean array
def draw_grid(array):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            color = WHITE if array[row * GRID_SIZE + col] else BLACK
            pygame.draw.rect(
                screen,
                color,
                (
                    GRID_ORIGIN[0] + col * (SQUARE_SIZE + MARGIN),
                    GRID_ORIGIN[1] + row * (SQUARE_SIZE + MARGIN),
                    SQUARE_SIZE,
                    SQUARE_SIZE,
                ),
            )


# Function to draw the boolean array
def draw_array(array):
    font = pygame.font.SysFont(None, ARRAY_FONT_SIZE)
    for i, val in enumerate(array):
        text = font.render(f"{val}", True, GRAY)
        screen.blit(
            text,
            (
                ARRAY_ORIGIN[0] + (i % GRID_SIZE) * 20,
                ARRAY_ORIGIN[1] + (i // GRID_SIZE) * 30,
            ),
        )


# Function to update the boolean array based on mouse position
def update_array(pos):
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            square_rect = pygame.Rect(
                GRID_ORIGIN[0] + col * (SQUARE_SIZE + MARGIN),
                GRID_ORIGIN[1] + row * (SQUARE_SIZE + MARGIN),
                SQUARE_SIZE,
                SQUARE_SIZE,
            )
            if square_rect.collidepoint(pos):
                index = row * GRID_SIZE + col
                boolean_array[index] = 0 if boolean_array[index] else 1
                return


# Game loop
running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.MOUSEBUTTONDOWN:
            update_array(pygame.mouse.get_pos())

    screen.fill(BLACK)
    draw_grid(boolean_array)
    draw_array(boolean_array)
    pygame.display.flip()

pygame.quit()
