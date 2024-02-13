import pygame
from settings import *
from animation import Animation
from slash_attack import SlashAttack


class Player(pygame.sprite.Sprite):
    def __init__(self, display):
        super().__init__()
        self.display = display
        self.sprite_sheet = pygame.image.load('Player_Sprite_Sheet2.png').convert_alpha()
        self.scale = 2

        animations = {
            'idle': (0, 3, 150),  # First row, frames 0-3
            'run': (4, 9, 120),  # First row, frames 4-7
        }
        self.animation = Animation(self.sprite_sheet, animations, (40, 40), self.scale)
        self.slash_attack = SlashAttack(self, offset_x=75, offset_y=0,
                                        sprite_sheet_path='path_to_slash_sprite_sheet.png',
                                        frame_dimensions=(50, 37), num_frames=4, scale=2)

        # Initially set to 'idle' animation
        self.animation.set_animation('idle')
        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect(center=DISPLAY_CENTER)

        self.last_slash = 0
        self.slash_cooldown = 1250

        # Player stats
        self.is_alive = True
        self.max_health = 100
        self.current_health = self.max_health
        self.speed = 2
        self.current_xp = 0
        self.xp_to_next_level = 100
        self.level_up_percentage = 100
        self.level = 1
        self.facing_right = True
        self.attacking = False
        self.attack_start_time = 0
        self.jumping = False

    def move(self):
        keys = pygame.key.get_pressed()
        moving = False

        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            moving = True
            self.animation.set_animation('run')
        else:
            self.animation.set_animation('idle')

        dx, dy = 0, 0
        if keys[pygame.K_RIGHT]:
            dx += self.speed
            self.facing_right = True
        if keys[pygame.K_LEFT]:
            dx -= self.speed
            self.facing_right = False
        if keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_DOWN]:
            dy += self.speed

        diagonal_movement = dx != 0 and dy != 0
        if diagonal_movement:
            dx *= DIAGONAL_SPEED_FACTOR
            dy *= DIAGONAL_SPEED_FACTOR

        self.rect.move_ip(dx, dy)

    def take_damage(self, amount):
        self.current_health -= amount

    def get_pos(self):
        return self.rect.topleft

    def increase_health(self, amount):
        self.current_health += amount
        if self.current_health >= self.max_health:
            self.current_health = self.max_health

    def increase_xp(self, amount):
        self.current_xp += amount
        while self.current_xp >= self.xp_to_next_level:
            self.level_up()

    def level_up(self):
        self.current_xp -= self.xp_to_next_level  # Reset experience towards the next level
        self.level += 1
        # Calculate new XP requirement for the next level
        self.xp_to_next_level = int(self.xp_to_next_level * (1 + self.level_up_percentage / 100.0))

    def draw(self):
        # Flip the image if facing left
        if not self.facing_right:
            flipped_image = pygame.transform.flip(self.image, True, False)
            self.display.blit(flipped_image, self.rect)
        else:
            self.display.blit(self.image, self.rect)

        self.slash_attack.draw(self.display)

    def reset(self):
        self.rect.topleft = DISPLAY_CENTER
        self.current_health = self.max_health

    def update(self):
        current_time = pygame.time.get_ticks()

        if current_time - self.last_slash > self.slash_cooldown:
            self.last_slash = current_time
            self.slash_attack.trigger_attack(self.facing_right)

        self.slash_attack.update()

        self.animation.update()
        self.image = self.animation.get_current_frame()
        if not self.facing_right:
            self.image = pygame.transform.flip(self.image, True, False)
        self.rect = self.image.get_rect(center=self.rect.center)
        self.move()
