import pygame
import random
from typing import Tuple, Optional

__all__ = ["SmartCamera"]
__version__ = "0.1.0"

class SmartCamera:
    """
    A smooth-follow and shake-enabled camera for Pygame games.

    Attach to a player object (with a `rect`), call `update()` each frame,
    and use `apply()` to offset your entities before drawing.
    """

    def __init__(self, player, display_size: Tuple[int, int], *,
                 auto_smooth: bool = True,
                 world_rect: Optional[pygame.Rect] = None):
        """
        Initialize the camera.

        Args:
            player: Object with a `rect` (pygame.Rect) representing position.
            display_size: (width, height) of the game window in pixels.
            auto_smooth: Whether to interpolate movement (default: True).
            world_rect: Optional world boundaries to clamp camera movement.
        """
        self.player = player
        self.display_width, self.display_height = display_size
        self.world_rect = world_rect

        self.offset_x = 0.0
        self.offset_y = 0.0
        self.target_x = 0.0
        self.target_y = 0.0

        self.auto_smooth = auto_smooth
        self.smoothness = 0.1

        self.shake_intensity = 0.0
        self.shake_timer = 0
        self.shake_offset_x = 0.0
        self.shake_offset_y = 0.0

    def update(self, dt: float = 1/60) -> None:
        """
        Update the camera position for the current frame.

        Args:
            dt: Time step in seconds since last update (default: 1/60).
        """
        # Center camera on player
        self.target_x = self.player.rect.centerx - self.display_width / 2
        self.target_y = self.player.rect.centery - self.display_height / 2

        # Clamp to world bounds if given
        if self.world_rect:
            max_x = self.world_rect.width - self.display_width
            max_y = self.world_rect.height - self.display_height
            self.target_x = max(0, min(self.target_x, max_x))
            self.target_y = max(0, min(self.target_y, max_y))

        # Smooth or instant movement
        if self.auto_smooth:
            alpha = 1 - (1 - self.smoothness) ** (dt * 60)
            self.offset_x += (self.target_x - self.offset_x) * alpha
            self.offset_y += (self.target_y - self.offset_y) * alpha
        else:
            self.offset_x, self.offset_y = self.target_x, self.target_y

        self._update_shake()

    def _update_shake(self) -> None:
        """Handle shake offset each frame."""
        if self.shake_timer > 0:
            self.shake_offset_x = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_offset_y = random.uniform(-self.shake_intensity, self.shake_intensity)
            self.shake_timer -= 1
        else:
            self.shake_offset_x = self.shake_offset_y = 0.0
            self.shake_timer = 0

    def apply(self, entity_or_rect) -> pygame.Rect:
        """
        Apply the camera offset to an entity or rect.

        Args:
            entity_or_rect: Object with a `rect` attribute or a pygame.Rect.

        Returns:
            pygame.Rect: Adjusted rect for rendering.
        """
        rect = entity_or_rect if isinstance(entity_or_rect, pygame.Rect) else entity_or_rect.rect
        ox = int(round(self.offset_x + self.shake_offset_x))
        oy = int(round(self.offset_y + self.shake_offset_y))
        return rect.move(-ox, -oy)

    def get_offset(self) -> Tuple[int, int]:
        """
        Get the current (x, y) offset applied by the camera.

        Returns:
            Tuple[int, int]: Camera offset including shake.
        """
        ox = int(round(self.offset_x + self.shake_offset_x))
        oy = int(round(self.offset_y + self.shake_offset_y))
        return (ox, oy)

    def add_shake(self, intensity: float = 5.0, duration: int = 20) -> None:
        """
        Trigger a manual shake effect.

        Args:
            intensity: Shake range in pixels (default: 5.0).
            duration: Duration in frames (default: 20).
        """
        self.shake_intensity = max(0.0, float(intensity))
        self.shake_timer = max(0, int(duration))

    def set_smoothness(self, smoothness: float) -> None:
        """
        Set the smoothing factor for camera motion.

        Args:
            smoothness: 0.0 = instant, 0.1 = default, 1.0 = very slow.
        """
        self.smoothness = max(0.0, min(1.0, float(smoothness)))

    def toggle_smooth(self) -> None:
        """Toggle smooth movement on or off."""
        self.auto_smooth = not self.auto_smooth

    def reset(self) -> None:
        """Instantly center the camera on the player and clear shake."""
        self.offset_x = self.player.rect.centerx - self.display_width / 2
        self.offset_y = self.player.rect.centery - self.display_height / 2
        self.target_x, self.target_y = self.offset_x, self.offset_y
        self.shake_timer = 0
        self.shake_offset_x = self.shake_offset_y = 0.0
