import pygame
from player import Player
from enemy_manager import EnemyManager
from scoreboard import Scoreboard
from health_bar import HealthBar
from settings import *
from pause_menu import PauseMenu

class Level:
    def __init__(self, display, game_state_manager, clock):
        self.display = display
        self.game_state_manager = game_state_manager
        self.player = Player(self.display)
        self.enemy_manager = EnemyManager(self.display, 20, 20)
        self.scoreboard = Scoreboard(self.display, clock)
        self.health_bar = HealthBar(self.display, self.player)
        self.pause_menu = PauseMenu(self.display, game_state_manager)

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.pause_menu.is_paused = not self.pause_menu.is_paused
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse button down events
                pass

    def check_collisions(self):
        hits = pygame.sprite.spritecollide(self.player, self.enemy_manager.enemy_list, True)
        for enemy in hits:
            self.player.take_damage(enemy.damage)



    def run(self, events):
        self.handle_events(events)

        if not self.pause_menu.is_paused:
            self.display.fill('black')
            self.player.update()
            self.enemy_manager.update(self.player.get_pos())
            self.check_collisions()
            self.scoreboard.update()
            self.health_bar.update()
        else:
            self.pause_menu.update(events)
            self.pause_menu.draw()