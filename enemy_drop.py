import pygame
import random

class EnemyDrop(pygame.sprite.Sprite):
    def __init__(self, display, pos, drop_type, scale=1):
        super().__init__()
        self.display = display
        self.pos = pos
        self.drop_type = drop_type
        self.scale = scale
        self.image = self.load_image(drop_type)
        self.rect = self.image.get_rect(center=pos)

    def load_image(self, drop_type):
        """Load different images based on the drop type."""
        if drop_type == 'health':
            image = pygame.image.load('red_potion.png').convert_alpha()
        elif drop_type == 'exp':
            image = pygame.image.load('emerald.png').convert_alpha()
        elif drop_type == 'money':
            image = pygame.image.load('money_drop.png').convert_alpha()
        else:
            # Fallback image or a default image for unknown types
            image = pygame.image.load('default_drop.png').convert_alpha()

        # Apply scaling if scale factor is not 1
        if self.scale != 1:
            image_width = image.get_width() * self.scale
            image_height = image.get_height() * self.scale
            image = pygame.transform.scale(image, (int(image_width), int(image_height)))

        return image

    @staticmethod
    def determine_drop_type():
        drop_types = ['health', 'exp', 'money']
        return drop_types[1]

    def update(self):
        # If you need to update the drop's state, do it here
        pass

    def draw(self, surface, offset):
        offset_pos = self.rect.topleft - offset
        surface.blit(self.image, offset_pos)
