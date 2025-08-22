import pygame
from settings import *

class SlashAttack(pygame.sprite.Sprite):
    def __init__(self, parent, offset_x, offset_y, sprite_sheet_path, frame_dimensions, num_frames, scale=1):
        super().__init__()
        self.parent = parent  # Reference to the player object
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.sprite_sheet = pygame.image.load('slash_anim.png').convert_alpha()
        self.frame_width, self.frame_height = frame_dimensions
        self.frames = self.load_frames(num_frames, scale)
        self.image = self.frames[0]
        self.rect = self.image.get_rect()
        self.active = False
        self.current_frame = 0
        self.last_update = pygame.time.get_ticks()
        self.animation_speed = 50  # Milliseconds per frame
        self.damage = 15  # Slash attack damage
        # Track enemies hit during the current slash so each is hit once per attack
        self._hit_targets = set()

    def load_frames(self, num_frames, scale):
        frames = []
        for frame_num in range(num_frames):
            frame_rect = pygame.Rect(
                frame_num * self.frame_width, 0,
                self.frame_width, self.frame_height
            )
            frame_image = self.sprite_sheet.subsurface(frame_rect).copy()
            frame_image = pygame.transform.scale(
                frame_image, (int(self.frame_width * scale), int(self.frame_height * scale))
            )
            frames.append(frame_image)
        return frames

    def trigger_attack(self, facing_right):
        if not self.active:
            self.active = True
            self.current_frame = 0
            self._hit_targets.clear()
            # Position the attack based on the parent's facing direction
            self.rect.centerx = self.parent.rect.centerx + (self.offset_x if facing_right else -self.offset_x)
            self.rect.centery = self.parent.rect.centery + self.offset_y
            # Flip frames if facing left
            if not facing_right:
                self.frames = [pygame.transform.flip(frame, True, False) for frame in self.frames]
            else:
                self.frames = self.load_frames(len(self.frames), self.parent.scale)

    def update(self):
        if self.active:
            now = pygame.time.get_ticks()
            if now - self.last_update > self.animation_speed:
                self.last_update = now
                self.current_frame += 1
                if self.current_frame >= len(self.frames):
                    self.active = False
                    self.current_frame = 0
                    self._hit_targets.clear()
                    self.frames = self.load_frames(len(self.frames), self.parent.scale)  # Reset frames to original
                else:
                    self.image = self.frames[self.current_frame]

    def has_hit(self, enemy) -> bool:
        return id(enemy) in self._hit_targets

    def mark_hit(self, enemy) -> None:
        self._hit_targets.add(id(enemy))

    def draw(self, surface, offset):
        if self.active:
            surface.blit(self.image, self.rect.topleft - pygame.math.Vector2(offset))
