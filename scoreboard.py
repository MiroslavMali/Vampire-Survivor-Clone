import pygame
from settings import *

class Scoreboard:
    def __init__(self, display, clock):
        self.display = display
        self.current_score = 0
        self.time_elapsed = pygame.time.get_ticks()
        self.font = pygame.font.SysFont(None, FONT_SIZE)
        self.time_delay = 1000
        self.score_increase = 1
        self.clock = clock
        # Hide legacy HUD by default (perf overlay replaces FPS; timer lives under XP bar)
        self.visible = False

    def reset(self):
        self.current_score = 0
        self.time_elapsed = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.time_elapsed >= self.time_delay:
            self.current_score += self.score_increase
            self.time_elapsed += self.time_delay
        if self.visible:
            self.score_surface = self.font.render(f"Score: {self.current_score}", False, 'white')
            fps_val = int(self.clock.get_fps()) if hasattr(self.clock, 'get_fps') else 0
            self.fps_surface = self.font.render(f"Fps: {fps_val}", False, 'white')
            self.draw_score()

    def draw_score(self):
        if not self.visible:
            return
        self.display.blit(self.score_surface, (20, 40))
        self.display.blit(self.fps_surface, (20, 80))
