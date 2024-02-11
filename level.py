import pygame
from player import Player
from enemy_manager import EnemyManager
from scoreboard import Scoreboard
from health_bar import HealthBar
from settings import *
from pause_menu import PauseMenu
from enemy_drop import EnemyDrop

class Level:
    def __init__(self, display, game_state_manager, clock):
        self.display = display
        self.game_state_manager = game_state_manager
        self.player = Player(self.display)
        self.enemy_manager = EnemyManager(self.display, 20, 20)
        self.scoreboard = Scoreboard(self.display, clock)
        self.health_bar = HealthBar(self.display, self.player)
        self.pause_menu = PauseMenu(self.display, game_state_manager)
        self.drops = pygame.sprite.Group()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_menu.is_paused = not self.pause_menu.is_paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse button down events
                pass

    def check_collisions(self):
        """Handle player / enemy collision"""
        hits = pygame.sprite.spritecollide(self.player, self.enemy_manager.enemy_list, True, collided=pygame.sprite.collide_rect_ratio(0.6))
        for enemy in hits:
            self.player.take_damage(enemy.damage)

    def check_slash_collisions(self):
        if self.player.slash_attack.active:
            enemies_hit = pygame.sprite.spritecollide(self.player.slash_attack, self.enemy_manager.enemy_list, dokill=True)
            for enemy in enemies_hit:
                self.scoreboard.current_score += 10  # Example of incrementing the score
                drop_type = 'health'  # Or determine the drop type based on some logic
                drop = EnemyDrop(self.display, enemy.rect.center, drop_type, 2)
                self.drops.add(drop)

    def check_drop_collisions(self):
        drops_hit = pygame.sprite.spritecollide(self.player, self.drops, dokill=True, collided=pygame.sprite.collide_rect_ratio(0.8))
        for drop in drops_hit:
            if drop.drop_type == 'health':
                self.player.increase_health(10)
            elif drop.drop_type == 'exp':
                self.player.gain_exp(100)
            # Handle other drop types as needed

    def collect_drop(self, drop):
        # Handle the effect of the drop
        if drop.drop_type == 'health':
            self.player.increase_health(10)  # Example method to increase player health
        elif drop.drop_type == 'exp':
            self.player.gain_exp(100)  # Example method to increase player XP
        # Add more conditions as needed

    def reset(self):
        self.player.reset()
        self.enemy_manager.reset()
        self.scoreboard.reset()

    def run(self, events):
        self.handle_events(events)

        if not self.pause_menu.is_paused:
            self.display.fill('black')
            self.player.update()
            self.enemy_manager.update(self.player.rect)
            self.check_collisions()
            self.check_slash_collisions()
            self.check_drop_collisions()
            self.drops.update()
            self.drops.draw(self.display)
            self.scoreboard.update()
            self.health_bar.update()
        else:
            self.pause_menu.update(events)
            self.pause_menu.draw()