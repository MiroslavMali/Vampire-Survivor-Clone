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

    def reset(self):
        self.current_score = 0
        self.time_elapsed = pygame.time.get_ticks()

    def update(self):
        current_time = pygame.time.get_ticks()
        if current_time - self.time_elapsed >= self.time_delay:
            self.current_score += self.score_increase
            self.time_elapsed += self.time_delay

        self.score_surface = self.font.render(f"Score: {self.current_score}", False, 'white')
        self.fps_surface = self.font.render(f"Fps: {self.clock}", False, 'white')
        self.draw_score()

    def draw_score(self):
        self.display.blit(self.score_surface, (20, 20))
        self.display.blit(self.fps_surface, (20, 40))
