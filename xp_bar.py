import pygame
from settings import FONT_SIZE

class XPBar:
    def __init__(self, display, player):
        self.display = display
        self.player = player
        self.margin_top = 10
        self.margin_side = 10
        self.height = 20
        self.outline_color = 'white'
        self.bar_color = 'blue'
        self.bg_color = 'black'
        self.font = pygame.font.SysFont('Arial', 18, True)
        # Timer styling: exactly match scoreboard font
        self.timer_font = pygame.font.SysFont(None, FONT_SIZE)
        self.timer_start_ms = pygame.time.get_ticks()
        self.timer_surface = None

    def update(self, current_xp, max_xp):
        # Render the level text only once in update
        self.level_surface = self.font.render(f"L E V E L : {self.player.level}", True, 'white')
        # Timer text in m:ss format since session start
        elapsed_ms = max(0, pygame.time.get_ticks() - self.timer_start_ms)
        seconds = elapsed_ms // 1000
        m, s = divmod(seconds, 60)
        self.timer_surface = self.timer_font.render(f"{m}:{s:02d}", False, 'white')
        self.draw(current_xp, max_xp)

    def draw(self, current_xp, max_xp):
        bar_width = self.display.get_width() - (self.margin_side * 2)
        exp_ratio = current_xp / max_xp if max_xp else 0
        filled_width = bar_width * exp_ratio

        # Draw background bar
        pygame.draw.rect(self.display, self.bg_color, (self.margin_side, self.margin_top, bar_width, self.height))
        # Draw filled bar
        pygame.draw.rect(self.display, self.bar_color, (self.margin_side, self.margin_top, filled_width, self.height))
        # Draw outline
        pygame.draw.rect(self.display, self.outline_color, (self.margin_side - 2, self.margin_top - 2, bar_width + 4, self.height + 4), 2)
        # Center the level text above the XP bar
        center_y = self.margin_top + self.height // 2
        level_rect = self.level_surface.get_rect(center=(self.display.get_width() // 2, center_y))
        self.display.blit(self.level_surface, level_rect)
        # Timer just beneath the bar, centered
        if self.timer_surface:
            timer_rect = self.timer_surface.get_rect(center=(self.display.get_width() // 2, self.margin_top + self.height + 18))
            self.display.blit(self.timer_surface, timer_rect)
