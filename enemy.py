import pygame
import math

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((20, 20))
        self.image.fill('green')
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x = float(x)
        self.y = float(y)

        # Enemy stats
        self.damage = 1
        self.speed = 0.5
        self.attack_cooldown = 100  # milliseconds
        self.last_attack_time = 0  # When the last attack occurred

    def move(self, player_pos):
        target_x, target_y = player_pos
        dx, dy = target_x - self.x, target_y - self.y
        distance = math.hypot(dx, dy)
        if distance > 0:
            dx, dy = dx / distance, dy / distance
            self.x += dx * self.speed
            self.y += dy * self.speed
        self.rect.x = int(self.x)
        self.rect.y = int(self.y)

    def can_attack(self, current_time):
        # Check if enough time has passed since the last attack
        return current_time - self.last_attack_time >= self.attack_cooldown

    def attack(self, player, current_time):
        # Damage the player if cooldown has passed
        if self.can_attack(current_time):
            player.take_damage(self.damage)
            self.last_attack_time = current_time

    def draw(self, surface, offset):
        offset_pos = self.rect.topleft - pygame.Vector2(offset)
        surface.blit(self.image, offset_pos)

    def update(self, player_pos, current_time):
        self.move(player_pos)
