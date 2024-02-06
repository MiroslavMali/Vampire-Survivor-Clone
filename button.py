import pygame

def adjust_color(color, amount):
    """Adjusts the brightness of the given color by the specified amount."""
    return tuple(max(0, min(255, component + amount)) for component in color)

class Button:
    def __init__(self, x, y, width, height, base_color, text, text_color, action=None, image=None):
        self.rect = pygame.Rect(x, y, width, height)
        self.base_color = base_color
        self.hover_color = adjust_color(base_color, -40)
        self.clicked_color = adjust_color(base_color, -80)
        self.text = text
        self.text_color = text_color
        self.action = action
        self.font = pygame.font.Font(None, 36)
        self.image = image
        if self.image:
            self.image = pygame.transform.scale(self.image, (width, height))

    def draw(self, screen):
        mouse_pos = pygame.mouse.get_pos()
        button_color = self.base_color

        if self.rect.collidepoint(mouse_pos):
            button_color = self.hover_color

        pygame.draw.rect(screen, button_color, self.rect, border_radius=10)
        if self.image:
            screen.blit(self.image, self.rect)
        else:
            self.draw_text(screen)

    def draw_text(self, screen):
        text_surface = self.font.render(self.text, True, self.text_color)
        text_rect = text_surface.get_rect(center=self.rect.center)
        screen.blit(text_surface, text_rect)

    def update(self, events):
        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and self.rect.collidepoint(event.pos):
                if self.action:
                    self.action()

    def is_over(self, pos):
        return self.rect.collidepoint(pos)
