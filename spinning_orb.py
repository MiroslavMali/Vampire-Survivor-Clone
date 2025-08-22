import pygame
import math

class SpinningOrb(pygame.sprite.Sprite):
    def __init__(self, player, radius, rotation_speed, damage):
        super().__init__()
        self.player = player
        self.radius = radius
        self.rotation_speed = rotation_speed  # Rotation speed in radians/frame
        self.damage = damage
        self.angle = 0
        # Use provided sprite for the orb (cached)
        self.image = _load_image_cached('orb.png')
        self.rect = self.image.get_rect(center=self.calculate_orb_position())

    def calculate_orb_position(self):
        # Calculate orb's position around the player
        orb_x = self.player.rect.centerx + math.cos(self.angle) * self.radius
        orb_y = self.player.rect.centery + math.sin(self.angle) * self.radius
        return orb_x, orb_y

    def update(self, dt):
        # Increment the angle
        self.angle += self.rotation_speed * dt
        # Ensure the angle doesn't exceed 2*pi
        self.angle %= 2 * math.pi
        # Update the orb's position
        self.rect.center = self.calculate_orb_position()

    def draw(self, surface, offset):
        # Adjust position by the camera's offset
        draw_pos = self.rect.topleft - pygame.Vector2(offset)
        surface.blit(self.image, draw_pos)


# --- Module-local image cache ---
_IMAGE_CACHE = {}

def _load_image_cached(path: str) -> pygame.Surface:
    surf = _IMAGE_CACHE.get(path)
    if surf is None:
        surf = pygame.image.load(path).convert_alpha()
        _IMAGE_CACHE[path] = surf
    return surf

