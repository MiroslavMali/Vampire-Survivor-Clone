import pygame
import math
from enemy_config import ENEMY_TYPES, DEFAULT_DROP

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, enemy_type='rat'):
        super().__init__()
        
        # Get configuration for this enemy type
        if enemy_type not in ENEMY_TYPES:
            enemy_type = 'rat'  # Default fallback
        config = ENEMY_TYPES[enemy_type]
        
        # Load sprite (cached)
        self.original_image = _load_image_cached(config['sprite'])
        self.image = self.original_image
        self.rect = self.image.get_rect(topleft=(x, y))
        # Track precise position as center coordinates for accurate steering
        self.center_x = float(self.rect.centerx)
        self.center_y = float(self.rect.centery)
        self.enemy_type = enemy_type

        # Enemy stats from configuration
        self.health = config['health']
        self.max_health = config['health']
        self.damage = config['damage']
        # Enemy speed is configured directly in pixels/second (px/s)
        self.speed = float(config['speed'])
        self.attack_cooldown = config['attack_cooldown']
        self.xp_value = config['xp_value']
        # Drop config with global defaults
        self.drop_chance = config.get('drop_chance', DEFAULT_DROP['chance'])
        self.drop_weights = config.get('drop_weights', DEFAULT_DROP['weights'])
        self.drop_types = config.get('drop_types', list(self.drop_weights.keys()))
        
        self.last_attack_time = 0
        self.facing_right = True
        # Movement gating when colliding/attacking
        self.stopped_due_to_attack = False
        
        # Damage feedback (white flash)
        self.damage_flash_time = 0
        self.damage_flash_duration = 350  # milliseconds
        # Precompute white flash overlay once from mask
        self._flash_overlay = _create_flash_overlay(self.original_image)

        # Knockback
        self.knockback_pixels = 10  # small instantaneous push distance
        self.knockback_vx = 0.0
        self.knockback_vy = 0.0
        self.knockback_impulse = 270.0  # pixels/sec initial push on hit (tuned)
        self.knockback_damping = 3.0    # lower = slower decay (more slide)

        # Death fade
        self.is_dying = False
        self.death_start_time = 0
        self.death_duration = 1000  # milliseconds
        self.has_dropped = False

    def move(self, player_pos):
        # Pursuit movement is disabled while colliding/attacking or dying,
        # but knockback sliding should still be applied.
        move_x, move_y = 0.0, 0.0
        # Per-enemy dt set in update()
        dt = getattr(self, "_dt", 0.0)

        if not (self.stopped_due_to_attack or self.is_dying):
            target_x, target_y = player_pos  # player center
            dx, dy = target_x - self.center_x, target_y - self.center_y
            distance = math.hypot(dx, dy)
            if distance > 0:
                ndx, ndy = dx / distance, dy / distance
                # dt-based movement; speed is pixels/second
                move_x += ndx * self.speed * dt
                move_y += ndy * self.speed * dt

        # Apply knockback velocity with simple damping using per-enemy dt
        if self.knockback_vx or self.knockback_vy:
            move_x += self.knockback_vx * dt
            move_y += self.knockback_vy * dt
            decay = max(0.0, 1.0 - self.knockback_damping * dt)
            self.knockback_vx *= decay
            self.knockback_vy *= decay

        self.center_x += move_x
        self.center_y += move_y
        # Sync rect from center position
        self.rect.centerx = int(self.center_x)
        self.rect.centery = int(self.center_y)

        if player_pos[0] < self.rect.centerx:  # If player is to the left
            self.image = pygame.transform.flip(self.original_image, True, False)
        else:  # If player is to the right
            self.image = self.original_image

    def can_attack(self, current_time):
        # Check if enough time has passed since the last attack
        if self.is_dying:
            return False
        return current_time - self.last_attack_time >= self.attack_cooldown

    def attack(self, player, current_time):
        # Damage the player if cooldown has passed
        if self.can_attack(current_time):
            player.take_damage(self.damage)
            self.last_attack_time = current_time

    def take_damage(self, amount, hit_source_pos=None):
        # Ignore further damage while fading out
        if self.is_dying:
            return False

        self.health -= amount
        self.damage_flash_time = pygame.time.get_ticks()  # Start damage flash

        # Apply knockback impulse away from the hit source if provided
        if hit_source_pos is not None:
            hx, hy = hit_source_pos
            dx = self.center_x - hx
            dy = self.center_y - hy
            distance = math.hypot(dx, dy)
            if distance > 0:
                ndx = dx / distance
                ndy = dy / distance
                # Small instant push
                self.center_x += ndx * self.knockback_pixels
                self.center_y += ndy * self.knockback_pixels
                # Sliding impulse
                self.knockback_vx += ndx * self.knockback_impulse
                self.knockback_vy += ndy * self.knockback_impulse
                self.rect.centerx = int(self.center_x)
                self.rect.centery = int(self.center_y)

        if self.health <= 0 and not self.is_dying:
            self.start_death()
            return True  # Signal death (for drop logic)
        return False

    def start_death(self):
        self.is_dying = True
        self.death_start_time = pygame.time.get_ticks()

    def draw(self, surface, offset):
        offset_pos = self.rect.topleft - pygame.Vector2(offset)
        current_time = pygame.time.get_ticks()

        # Base frame (already flipped/set in move())
        frame = self.image

        # Determine if we need a copy (flash or death fade)
        do_flash = (current_time - self.damage_flash_time) < self.damage_flash_duration
        do_death_fade = self.is_dying
        if do_flash or do_death_fade:
            frame = frame.copy()
            if do_flash and self._flash_overlay is not None:
                # If current frame is flipped relative to original, flip overlay to match
                is_flipped = (frame.get_bitsize() == self.original_image.get_bitsize()) and (
                    frame.get_width() == self.original_image.get_width() and frame.get_height() == self.original_image.get_height()
                ) and (frame.get_locked() == self.original_image.get_locked())
                # Heuristic is unreliable; simply flip based on player facing: image was flipped in move() when player is left
                overlay = self._flash_overlay
                if self.image is not self.original_image:
                    overlay = pygame.transform.flip(overlay, True, False)
                frame.blit(overlay, (0, 0), special_flags=pygame.BLEND_RGBA_ADD)
            if do_death_fade:
                elapsed = current_time - self.death_start_time
                if elapsed >= self.death_duration:
                    self.kill()
                    return
                alpha = max(0, 255 - int(255 * (elapsed / self.death_duration)))
                frame.set_alpha(alpha)

        surface.blit(frame, offset_pos)
        

    def update(self, player_pos, current_time):
        # Compute per-enemy dt (seconds) for smooth knockback without changing callers
        last = getattr(self, "_last_update_time", None)
        if last is None:
            dt = 0.0
        else:
            dt = max(0.0, (current_time - last) / 1000.0)
        # Clamp dt to avoid large catch-up steps (e.g., after pause)
        if dt > 0.05:
            dt = 0.05
        self._dt = dt
        self._last_update_time = current_time
        self.move(player_pos)


# --- Module-local image cache and helpers ---
_IMAGE_CACHE = {}

def _load_image_cached(path: str) -> pygame.Surface:
    surf = _IMAGE_CACHE.get(path)
    if surf is None:
        surf = pygame.image.load(path).convert_alpha()
        _IMAGE_CACHE[path] = surf
    return surf

def _create_flash_overlay(base_surface: pygame.Surface) -> pygame.Surface:
    try:
        mask = pygame.mask.from_surface(base_surface)
        return mask.to_surface(setcolor=(255, 255, 255, 220), unsetcolor=(0, 0, 0, 0))
    except Exception:
        return None
