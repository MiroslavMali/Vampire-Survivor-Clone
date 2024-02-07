import pygame, random
from settings import *
from enemy import Enemy

class EnemyManager:
    def __init__(self, display, sprite_width, sprite_height):
        self.display = display
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.enemy_list = pygame.sprite.Group()
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 1000

    def spawn_enemy(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time >= self.spawn_delay:
            x, y = get_random_XY(self)
            self.enemy_list.add(Enemy(x, y))
            self.last_spawn_time = current_time

    def reset(self):
        self.enemy_list.empty()
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 1000

    def draw(self, display):
        self.enemy_list.draw(display)

    def update(self, player_pos):
        self.spawn_enemy()
        self.enemy_list.update(player_pos)
        self.draw(self.display)
