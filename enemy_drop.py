import pygame
import random
from enemy_config import DROP_TYPES

class EnemyDrop(pygame.sprite.Sprite):
    def __init__(self, display, position, drop_type, scale=1, duration=5000):
        super().__init__()
        self.display = display
        self.drop_type = drop_type
        self.scale = scale
        self.duration = duration
        self.start_time = pygame.time.get_ticks()
        
        # Get drop properties from config
        drop_config = DROP_TYPES.get(drop_type, DROP_TYPES['exp'])
        self.value = drop_config['value']
        self.sprite_path = drop_config['sprite']
        
        # Load sprite with fallback (cached)
        try:
            self.image = _load_image_cached(self.sprite_path)
        except Exception:
            # Fallback to emerald if sprite not found
            self.image = _load_image_cached('emerald.png')
        
        # Apply scaling
        if self.scale != 1:
            image_width = int(self.image.get_width() * self.scale)
            image_height = int(self.image.get_height() * self.scale)
            self.image = pygame.transform.scale(self.image, (image_width, image_height))
        
        # Set rect based on scaled image
        self.rect = self.image.get_rect(center=position)
        # Float position for smooth movement
        self.pos_x = float(self.rect.centerx)
        self.pos_y = float(self.rect.centery)
        
        # Magnetic attraction properties (px/sec and px/sec^2)
        self.attraction_speed = 600.0
        self.attraction_acceleration = 1200.0
        self.current_speed = 0.0

        # Collect animation state (visual bounce then return)
        self.state = 'idle'  # 'idle' | 'bounce' | 'returning'
        self.ready_to_apply = False
        self.kb_vx = 0.0
        self.kb_vy = 0.0
        # Match enemy knockback feel
        self.kb_impulse = 350  # pixels/sec initial push
        self.kb_damping = 3.0     # slower decay for smooth slide
        self.bounce_time_ms = 200
        self.bounce_start_time = 0

    def force_return_to_player(self, player_center):
        """Immediately switch to homing back to the player, skipping bounce."""
        self.state = 'returning'
        self.ready_to_apply = False
        # Stop any knockback sliding
        self.kb_vx = 0.0
        self.kb_vy = 0.0
        # Give a reasonable initial speed so it starts moving right away
        self.current_speed = min(300.0, getattr(self, 'attraction_speed', 600.0))
        # Small nudge away from current position toward player to avoid zero-length vectors
        try:
            direction = (pygame.math.Vector2(player_center) - pygame.math.Vector2(self.rect.center)).normalize()
        except ValueError:
            direction = pygame.math.Vector2(1, 0)
        self.pos_x += direction.x * 2
        self.pos_y += direction.y * 2
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)
        
    def update_magnetic_attraction(self, player_rect, magnetic_radius):
        """Trigger collect when within magnetic radius (no movement here)."""
        if self.state != 'idle':
            return
        drop_center = pygame.math.Vector2(self.rect.center)
        player_center = pygame.math.Vector2(player_rect.center)
        distance = drop_center.distance_to(player_center)
        if distance <= magnetic_radius:
            self.start_collect(player_center)

    def start_collect(self, player_center):
        """Begin visual collect: bounce away from player then return to pick up."""
        if self.state != 'idle':
            return
        self.state = 'bounce'
        self.ready_to_apply = False
        self.bounce_start_time = pygame.time.get_ticks()
        dir_vec = pygame.math.Vector2(self.rect.center) - pygame.math.Vector2(player_center)
        if dir_vec.length_squared() == 0:
            dir_vec = pygame.math.Vector2(1, 0)
        dir_vec = dir_vec.normalize()
        # small instant nudge for responsiveness (exaggerated)
        self.pos_x += dir_vec.x * 12
        self.pos_y += dir_vec.y * 12
        # sliding impulse
        self.kb_vx += dir_vec.x * self.kb_impulse
        self.kb_vy += dir_vec.y * self.kb_impulse
        # sync rect
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

    def update_collect(self, player_rect, dt: float):
        """Update collect animation; sets ready_to_apply when returned to player."""
        if self.state == 'idle':
            return
        if self.state == 'bounce':
            # Apply knockback slide with damping (use level frame dt if available for consistency)
            dt = getattr(getattr(self, 'display', None), 'frame_dt', dt) if False else dt
            dt = min(dt, 0.033)
            self.pos_x += self.kb_vx * dt
            self.pos_y += self.kb_vy * dt
            decay = max(0.0, 1.0 - self.kb_damping * dt)
            self.kb_vx *= decay
            self.kb_vy *= decay
            if pygame.time.get_ticks() - self.bounce_start_time >= self.bounce_time_ms:
                self.state = 'returning'
                # Give a head start so it doesn't feel stuck
                self.current_speed = min(200.0, self.attraction_speed)
        elif self.state == 'returning':
            # Home in to the player center
            drop_center = pygame.math.Vector2(self.pos_x, self.pos_y)
            player_center = pygame.math.Vector2(player_rect.center)
            to_player = player_center - drop_center
            distance = to_player.length()
            if distance <= 8:
                self.ready_to_apply = True
                self.state = 'idle'
                return
            if distance > 0:
                direction = to_player.normalize()
                # Reuse attraction parameters (dt-based)
                dt = min(dt, 0.033)
                self.current_speed += self.attraction_acceleration * dt
                self.current_speed = min(self.current_speed, self.attraction_speed)
                # Move using speed (px/sec) scaled by dt
                self.pos_x += direction.x * self.current_speed * dt
                self.pos_y += direction.y * self.current_speed * dt
        # sync rect from float pos
        self.rect.centerx = int(self.pos_x)
        self.rect.centery = int(self.pos_y)

    @staticmethod
    def determine_drop_type(enemy_drop_types=None, enemy_drop_weights=None):
        """Determine drop type based on enemy configuration or random selection."""
        if enemy_drop_types and enemy_drop_weights:
            # Use enemy's specific drop types with weights
            return random.choices(enemy_drop_types, weights=list(enemy_drop_weights.values()))[0]
        elif enemy_drop_types:
            # Use enemy's specific drop types (equal chance)
            return random.choice(enemy_drop_types)
        else:
            # Random selection from all available drop types
            drop_types = list(DROP_TYPES.keys())
            return random.choice(drop_types)

    def draw(self, surface, offset):
        """Draw the drop on the surface with camera offset."""
        offset_pos = pygame.math.Vector2(self.rect.topleft) - pygame.math.Vector2(offset)
        surface.blit(self.image, offset_pos)


# --- Module-local image cache ---
_IMAGE_CACHE = {}

def _load_image_cached(path: str) -> pygame.Surface:
    surf = _IMAGE_CACHE.get(path)
    if surf is None:
        surf = pygame.image.load(path).convert_alpha()
        _IMAGE_CACHE[path] = surf
    return surf
