from button import Button
from settings import *
import pygame

class PauseMenu:
    def __init__(self, display, game_state_manager):
        # Initialize pause menu components (buttons, backgrounds, etc.)
        self.display = display
        self.game_manager = game_state_manager
        self.is_paused = False

        # Button specifications
        button_width, button_height = 200, 50
        button_x = DISPLAY_CENTER[0] - button_width // 2
        start_button_y = DISPLAY_HEIGHT // 2 - button_height - 10  # Above center
        quit_button_y = DISPLAY_HEIGHT // 2 + 10  # Below center

        # Creating buttons
        self.buttons = [
            Button(button_x, start_button_y, button_width, button_height, (88, 214, 141) , "Resume", (255, 255, 255), self.resume_game),
            Button(button_x, quit_button_y, button_width, button_height, (199, 0, 57), "Back to Menu", (255, 255, 255), self.quit_game)
        ]

        # Pause menu specifications
        self.margin_x = DISPLAY_WIDTH // 4
        self.margin_y = DISPLAY_HEIGHT // 4
        self.pause_surface = pygame.Surface((self.margin_x * 2, self.margin_y * 2))
        self.pause_surface.set_alpha(20)

    def resume_game(self):
        self.is_paused = not self.is_paused

    def quit_game(self):
        self.game_manager.set_state('main_menu')
        self.is_paused = False


    def update(self, events):
        # Update logic for pause menu
        for button in self.buttons:
            button.update(events)

    def draw(self):
        # Draw pause menu and its components
        for button in self.buttons:
            button.draw(self.display)

        self.pause_surface.fill('gray25')
        self.display.blit(self.pause_surface, (self.margin_x, self.margin_y))