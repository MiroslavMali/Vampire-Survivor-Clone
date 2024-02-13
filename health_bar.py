import pygame


class HealthBar:
    def __init__(self, display, player):
        self.display = display
        self.player = player
        self.bar_length = 50  # Length of the health bar
        self.bar_height = 5  # Height of the health bar
        self.offset = 0  # Offset of the health bar above the player

    def draw(self, offset):
        health_percentage = self.player.current_health / self.player.max_health
        health_bar_width = self.bar_length * health_percentage

        # Apply camera offset to the health bar's position
        bar_x = self.player.rect.centerx - self.bar_length // 2 - offset[0]
        bar_y = self.player.rect.bottom - self.offset - offset[1]

        # Now draw the health bar using the offset position
        pygame.draw.rect(self.display, (255, 0, 0), (bar_x, bar_y, self.bar_length, self.bar_height))
        pygame.draw.rect(self.display, (53, 94, 59), (bar_x, bar_y, health_bar_width, self.bar_height))

    def update(self, offset):
        self.draw(offset)
