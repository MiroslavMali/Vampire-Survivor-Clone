import pygame
from settings import *

class Player(pygame.sprite.Sprite):
    def __init__(self, display):
        super().__init__()
        self.display = display
        self.image = pygame.Surface((20, 20))
        self.image.fill('red')
        self.rect = self.image.get_rect(topleft=DISPLAY_CENTER)

        self.is_facing_right = True
        self.is_attacking = False

        # Player stats
        self.is_alive = True
        self.max_health = 100
        self.current_health = self.max_health
        self.speed = 1.5 # won't work unless lower than 1.4

    def move(self):
        keys = pygame.key.get_pressed()
        dx, dy = 0, 0
        if keys[pygame.K_RIGHT]:
            dx += self.speed
        if keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        diagonal_movement = dx != 0 and dy != 0
        if diagonal_movement:
            dx *= DIAGONAL_SPEED_FACTOR
            dy *= DIAGONAL_SPEED_FACTOR

        self.rect.move_ip(dx, dy)

    def take_damage(self, amount):
        self.current_health -= amount

    def get_pos(self):
        return self.rect.topleft

    def draw(self):
        pygame.draw.rect(self.display, 'red', self.rect)

    def reset(self):
        self.rect.topleft = DISPLAY_CENTER
        self.current_health = self.max_health

    def update(self):
        self.move()
        self.draw()
