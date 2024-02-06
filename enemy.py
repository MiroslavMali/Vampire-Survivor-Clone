import pygame
import math  # Ensure math is imported for hypot()

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill('green')
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = float(x)  # Initialize floating-point coordinates
        self.y = float(y)

        # Enemy stats
        self.damage = 8
        self.speed = 0.5

    def move(self, player_pos):
        # Calculate the direction vector towards the player
        dx, dy = player_pos[0] - self.x, player_pos[1] - self.y
        distance = math.hypot(dx, dy)
        # Avoid division by zero
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.x += dx * self.speed
            self.y += dy * self.speed
            # Update the rect position
            self.rect.x = int(self.x)
            self.rect.y = int(self.y)
        else:
            # If the enemy is exactly at the player's position, you might want to handle it differently
            pass

    def update(self, player_pos):
        self.move(player_pos)
