import pygame
from enemy import Enemy
from enemy_config import ENEMY_TYPES, ENEMY_SPAWN_WEIGHTS, LEVEL_UNLOCKS
import random

class EnemyManager:
    def __init__(self, display, sprite_width, sprite_height, default_spawn_delay=500):
        self.display = display
        self.sprite_width = sprite_width
        self.sprite_height = sprite_height
        self.enemy_list = pygame.sprite.Group()
        self.default_spawn_delay = default_spawn_delay
        self.current_spawn_delay = self.default_spawn_delay
        self.last_spawn_time = pygame.time.get_ticks()
        
        # Enemy spawning configuration
        self.enemy_spawn_weights = ENEMY_SPAWN_WEIGHTS
        
        # Level-based spawning (unlock new enemies as player levels up)
        self.level_unlocks = LEVEL_UNLOCKS

    def get_random_XY(self, camera_offset):
        spawn_margin = 50
        camera_offset_x, camera_offset_y = camera_offset

        spawn_side = random.choice(["horizontal", "vertical"])
        if spawn_side == "horizontal":
            y = random.randint(camera_offset_y - spawn_margin, camera_offset_y + self.display.get_height() + spawn_margin)
            x = random.choice([camera_offset_x - self.sprite_width - spawn_margin, camera_offset_x + self.display.get_width() + spawn_margin])
        else:
            x = random.randint(camera_offset_x - spawn_margin, camera_offset_x + self.display.get_width() + spawn_margin)
            y = random.choice([camera_offset_y - self.sprite_height - spawn_margin, camera_offset_y + self.display.get_height() + spawn_margin])
        return x, y

    def get_available_enemy_types(self, player_level):
        """Get enemy types available at the current player level"""
        available_types = ['rat']  # Always available
        
        for unlock_level, enemy_types in self.level_unlocks.items():
            if player_level >= unlock_level:
                available_types = enemy_types
                
        return available_types

    def choose_enemy_type(self, player_level):
        """Choose which enemy type to spawn based on weights and player level"""
        available_types = self.get_available_enemy_types(player_level)
        
        # Filter weights to only include available enemy types
        available_weights = {k: v for k, v in self.enemy_spawn_weights.items() if k in available_types}
        
        # If no weights available, default to rat
        if not available_weights:
            return 'rat'
            
        # Choose based on weights
        total_weight = sum(available_weights.values())
        random_value = random.randint(1, total_weight)
        
        current_weight = 0
        for enemy_type, weight in available_weights.items():
            current_weight += weight
            if random_value <= current_weight:
                return enemy_type
                
        return 'rat'  # Fallback

    def spawn_enemy(self, camera_offset, player_level=1):
        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time >= self.current_spawn_delay:
            x, y = self.get_random_XY(camera_offset)
            enemy_type = self.choose_enemy_type(player_level)
            self.enemy_list.add(Enemy(x, y, enemy_type))
            self.last_spawn_time = current_time

    def adjust_spawn_rate(self, player_level):
        """Dynamically adjust spawn rate based on player level.

        Increase spawn rate by 50% per level (exponential growth),
        implemented by dividing the base delay by 1.5^(level-1), with a 100 ms floor.
        """
        try:
            factor = 1.5 ** max(0, player_level - 1)
        except Exception:
            factor = 1.0
        new_delay = int(self.default_spawn_delay / factor)
        self.current_spawn_delay = max(100, new_delay)

    def reset(self):
        self.enemy_list.empty()
        self.last_spawn_time = pygame.time.get_ticks()
        self.current_spawn_delay = self.default_spawn_delay  # Reset spawn delay to default

    def draw(self, display, offset):
        for enemy in self.enemy_list:
            enemy.draw(display, offset)

    def update(self, player_pos, offset, current_time, player_level=1):
        self.adjust_spawn_rate(player_level)
        self.spawn_enemy(offset, player_level)
        for enemy in self.enemy_list:
            enemy.update(player_pos, current_time)
        self.draw(self.display, offset)
