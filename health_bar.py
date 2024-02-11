import pygame


class HealthBar:
    def __init__(self, display, player):
        self.display = display
        self.player = player
        self.bar_length = 50  # Length of the health bar
        self.bar_height = 5  # Height of the health bar
        self.offset = 0  # Offset of the health bar above the player

    def draw(self):
        # Calculate the health bar's width based on the player's current health
        health_percentage = self.player.current_health / self.player.max_health
        health_bar_width = self.bar_length * health_percentage

        # Calculate the position of the health bar (centered below the player)
        bar_x = self.player.rect.centerx - self.bar_length // 2
        bar_y = self.player.rect.bottom - self.offset  # Positioned below the player

        # Draw the background of the health bar
        pygame.draw.rect(self.display, (255, 0, 0), (bar_x, bar_y, self.bar_length, self.bar_height))

        # Draw the foreground of the health bar
        pygame.draw.rect(self.display, (53, 94, 59), (bar_x, bar_y, health_bar_width, self.bar_height))

    def update(self):
        self.draw()
