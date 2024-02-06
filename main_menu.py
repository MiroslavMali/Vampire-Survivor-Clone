import pygame, sys
from settings import *
from button import Button

class MainMenu:
    def __init__(self, display, game_state_manager):
        self.display = display
        self.game_state_manager = game_state_manager
        self.image = pygame.image.load('main_menu_bg.jpg')
        self.image = pygame.transform.scale(self.image, (DISPLAY_WIDTH, DISPLAY_HEIGHT))

        # Button specifications
        button_width, button_height = 200, 50
        button_x = DISPLAY_WIDTH - button_width - 300  # Right align, 30px from edge
        start_button_y = DISPLAY_HEIGHT // 2 - button_height - 60  # Above center
        settings_button_y = DISPLAY_HEIGHT // 2 - button_height + 10
        quit_button_y = DISPLAY_HEIGHT // 2 + 30  # Below center

        # Creating buttons
        self.buttons = [
            Button(button_x, start_button_y, button_width, button_height, (0, 255, 0), "Start", (255, 255, 255), self.start_game),
            Button(button_x, settings_button_y, button_width, button_height, (0, 0, 255), "Settings", (255, 255, 255), self.settings),
            Button(button_x, quit_button_y, button_width, button_height, (255, 0, 0), "Quit", (255, 255, 255), self.quit_game)
        ]

    def start_game(self):
        self.game_state_manager.set_state('level')

    def settings(self):
        print("settings")

    def quit_game(self):
        pygame.quit()
        sys.exit()

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            for button in self.buttons:
                button.update(events)

    def run(self, events):
        self.display.blit(self.image, (0, 0))
        self.handle_events(events)
        for button in self.buttons:
            button.draw(self.display)
