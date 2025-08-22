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
                                        sprite_sheet_path='slash_anim.png',
                                        frame_dimensions=(50, 37), num_frames=4, scale=2)

        # Initially set to 'idle' animation
        self.animation.set_animation('idle')
        self.image = self.animation.get_current_frame()
        self.rect = self.image.get_rect(center=DISPLAY_CENTER)
        self.position = pygame.math.Vector2(self.rect.center)

        self.last_slash = 0
        self.slash_cooldown = 1250

        # Player stats
        self.is_alive = True
        self.max_health = 100
        self.current_health = self.max_health
        self.speed = 180
        self.xp_multiplier = 1.0
        self.current_xp = 0
        self.xp_to_next_level = 100
        self.level_up_percentage = 25  # Reduced from 100 to 25 (25% increase per level)
        self.level = 1
        self.facing_right = True
        self.attacking = False
        self.attack_start_time = 0
        self.jumping = False

        # Magnetic field system
        self.magnetic_radius = 50  # Base radius set equal to first upgrade value
        self.magnetic_strength = 1.0  # How fast drops are attracted
        self.magnet_power_up_active = False
        self.magnet_power_up_duration = 0
        self.magnet_power_up_timer = 0

    def move(self, dt):
        keys = pygame.key.get_pressed()
        # Determine animation based on input

        if keys[pygame.K_RIGHT] or keys[pygame.K_LEFT] or keys[pygame.K_UP] or keys[pygame.K_DOWN]:
            self.animation.set_animation('run')
        else:
            self.animation.set_animation('idle')

        dx, dy = 0.0, 0.0
        pixels = self.speed * dt
        if keys[pygame.K_RIGHT]:
            dx += pixels
            self.facing_right = True
        if keys[pygame.K_LEFT]:
            dx -= pixels
            self.facing_right = False
        if keys[pygame.K_UP]:
            dy -= pixels
        if keys[pygame.K_DOWN]:
            dy += pixels

        diagonal_movement = dx != 0 and dy != 0
        if diagonal_movement:
            dx *= DIAGONAL_SPEED_FACTOR
            dy *= DIAGONAL_SPEED_FACTOR

        # Update float position then sync rect center
        self.position.x += dx
        self.position.y += dy
        self.rect.center = (round(self.position.x), round(self.position.y))

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

    # def draw(self):
    #     # Flip the image if facing left
    #     if not self.facing_right:
    #         flipped_image = pygame.transform.flip(self.image, True, False)
    #         self.display.blit(flipped_image, self.rect)
    #     else:
    #         self.display.blit(self.image, self.rect)
    #
    #     self.slash_attack.draw(self.display)

    def reset(self):
        self.rect.center = DISPLAY_CENTER
        self.position = pygame.math.Vector2(self.rect.center)
        self.current_health = self.max_health

    def update(self, dt):
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
        self.move(dt)

    def get_magnetic_radius(self):
        """Get current magnetic radius (increased during power-up)."""
        if self.magnet_power_up_active:
            return 300  # Large radius during power-up
        return self.magnetic_radius

    def activate_magnet_power_up(self, duration=5000):
        """Activate magnet power-up for specified duration (in milliseconds)."""
        self.magnet_power_up_active = True
        self.magnet_power_up_duration = duration
        self.magnet_power_up_timer = pygame.time.get_ticks()

    def update_magnet_power_up(self):
        """Update magnet power-up timer."""
        if self.magnet_power_up_active:
            current_time = pygame.time.get_ticks()
            if current_time - self.magnet_power_up_timer > self.magnet_power_up_duration:
                self.magnet_power_up_active = False
