import pygame
import math

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
        # player_pos is expected to be a tuple (x, y)
        target_x, target_y = player_pos  # Directly use player_pos without trying to access .center

        # Calculate the direction vector towards the player's position
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.hypot(dx, dy)
        # Normalize the direction vector
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.x += dx * self.speed
            self.y += dy * self.speed

        # Update the rect position
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def draw(self, surface, offset):
        offset_pos = self.rect.topleft - pygame.Vector2(offset)
        surface.blit(self.image, offset_pos)

    def update(self, player_pos):
        self.move(player_pos)
