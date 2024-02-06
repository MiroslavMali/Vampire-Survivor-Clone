import pygame
from settings import *

class HealthBar:
    def __init__(self, display, player):
        self.display = display
        self.player = player

    def draw(self):
        factor = self.player.current_health / 100
        pygame.draw.rect(self.display, 'white', (60 - 3, DISPLAY_HEIGHT - 60 - 3, 200 + 6, 20 + 6))
        pygame.draw.rect(self.display, (210, 43, 43), (60, DISPLAY_HEIGHT - 60, 200, 20))
        pygame.draw.rect(self.display, (53, 94, 59), (60, DISPLAY_HEIGHT - 60, 200 * factor, 20))

    def update(self):
        self.draw()