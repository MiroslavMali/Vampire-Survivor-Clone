import math
import random
import pygame

# Display settings
DISPLAY_WIDTH = 1280
DISPLAY_HEIGHT = 960
DISPLAY_CENTER = (DISPLAY_WIDTH/2, DISPLAY_HEIGHT/2)
FONT_SIZE = 28

# Movement factors
DIAGONAL_SPEED_FACTOR = math.sqrt(2) / 2


# Display functions
def get_random_XY(self):
    spawn_side = random.choice(["horizontal", "vertical"])
    if spawn_side == "horizontal":
        y = random.randint(0, DISPLAY_HEIGHT)
        x = random.choice([-self.sprite_width, DISPLAY_WIDTH + self.sprite_width])
    else:
        x = random.randint(0, DISPLAY_WIDTH)
        y = random.choice([-self.sprite_height, DISPLAY_HEIGHT + self.sprite_height])
    return x, y

# Both methods below were in main.py

# def update_display_surface(self):
#     # This method updates the display surface to match the current settings
#     self.display_surface = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))

# def change_resolution(event):
#     if event.key == pygame.K_1:
#         global DISPLAY_WIDTH
#         global DISPLAY_HEIGHT
#         DISPLAY_WIDTH = 1920
#         DISPLAY_HEIGHT = 1080
#         self.update_display_surface()
#     if event.key == pygame.K_2:
#         DISPLAY_WIDTH = 1280
#         DISPLAY_HEIGHT = 720
#         self.update_display_surface()