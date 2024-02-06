import pygame, sys
from settings import *
from game_state_manager import GameStateManager
from main_menu import MainMenu
from level import Level

class Main:
    def __init__(self):
        pygame.init()
        self.display_surface = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        self.clock = pygame.time.Clock()

        # Initialize scenes objects
        self.game_state_manager = GameStateManager('main_menu')
        self.main_menu = MainMenu(self.display_surface, self.game_state_manager)
        self.level = Level(self.display_surface, self.game_state_manager, self.clock)
        self.states = {'main_menu': self.main_menu, 'level': self.level}

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

    def draw(self):
        self.display_surface.fill('black')

    def run(self):
        while True:
            # System
            self.clock.tick(60)

            # Event handle
            events = pygame.event.get()
            self.handle_events(events)

            # State handle
            self.states[self.game_state_manager.get_state()].run(events)

            pygame.display.update()

if __name__ == '__main__':
    Main().run()
