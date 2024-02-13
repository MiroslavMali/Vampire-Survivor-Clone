import pygame
from enemy import Enemy
import random

class EnemyManager:
    def __init__(self, display, sprite_width, sprite_height):
        self.display = display
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.enemy_list = pygame.sprite.Group()
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 1000

    def get_random_XY(self, camera_offset):
        spawn_margin = 50  # Margin outside the camera view where enemies can spawn
        camera_offset_x, camera_offset_y = camera_offset

        spawn_side = random.choice(["horizontal", "vertical"])
        if spawn_side == "horizontal":
            y = random.randint(camera_offset_y - spawn_margin,
                               camera_offset_y + self.display.get_height() + spawn_margin)
            x = random.choice([camera_offset_x - self.sprite_width - spawn_margin,
                               camera_offset_x + self.display.get_width() + spawn_margin])
        else:
            x = random.randint(camera_offset_x - spawn_margin,
                               camera_offset_x + self.display.get_width() + spawn_margin)
            y = random.choice([camera_offset_y - self.sprite_height - spawn_margin,
                               camera_offset_y + self.display.get_height() + spawn_margin])
        return x, y

    def spawn_enemy(self, camera_offset):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time >= self.spawn_delay:
            x, y = self.get_random_XY(camera_offset)
            self.enemy_list.add(Enemy(x, y))
            self.last_spawn_time = current_time

    def reset(self):
        self.enemy_list.empty()
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 1000

    def draw(self, display, offset):
        for enemy in self.enemy_list:
            enemy.draw(display, offset)

    def update(self, player_pos, offset, current_time):
        self.spawn_enemy(offset)
        for enemy in self.enemy_list:
            enemy.update(player_pos, current_time)  # Ensure the Enemy class's update method accepts this argument
        self.draw(self.display, offset)