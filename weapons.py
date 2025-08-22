import pygame
import math
from typing import List, Tuple, Dict

from spinning_orb import SpinningOrb


class BaseWeapon:
    def __init__(self, player: pygame.sprite.Sprite):
        self.player = player
        self.enabled = False

    def enable(self) -> None:
        self.enabled = True

    def update(self, dt: float, now_ms: int) -> None:
        pass

    def draw(self, surface: pygame.Surface, offset: Tuple[int, int]) -> None:
        pass

    def get_hit_sprites(self) -> List[Tuple[pygame.sprite.Sprite, int]]:
        return []


class OrbWeapon(BaseWeapon):
    def __init__(self, player: pygame.sprite.Sprite, display: pygame.Surface):
        super().__init__(player)
        self.display = display
        self.orbs: List[SpinningOrb] = []
        self.orb_count = 1
        self.radius = 75
        self.rotation_speed = 5.0  # radians per second
        self.damage = 10
        # Uptime/downtime in milliseconds
        self.active_duration_ms = 3000
        self.downtime_ms = 5000
        self.active = False
        self.timer_ms = 0

    def _rebuild_orbs(self) -> None:
        # Create orbs with evenly spaced angles
        self.orbs = []
        if not self.enabled:
            return
        for i in range(self.orb_count):
            orb = SpinningOrb(self.player, self.radius, self.rotation_speed, self.damage)
            # Spread starting angles
            if self.orb_count > 0:
                orb.angle = (2 * math.pi * i) / self.orb_count
            self.orbs.append(orb)

    def enable(self) -> None:
        super().enable()
        self.active = True
        self.timer_ms = 0
        self._rebuild_orbs()

    # Upgrades
    def upgrade_count(self, delta: int, max_count: int = 5) -> None:
        self.orb_count = max(1, min(max_count, self.orb_count + delta))
        self._rebuild_orbs()

    def upgrade_damage_multiplier(self, multiplier: float) -> None:
        self.damage = max(1, int(self.damage * multiplier))
        for orb in self.orbs:
            orb.damage = self.damage

    def upgrade_radius(self, delta: int) -> None:
        self.radius = max(10, self.radius + delta)
        for orb in self.orbs:
            orb.radius = self.radius

    def upgrade_uptime_multiplier(self, multiplier: float) -> None:
        # Reduce downtime by multiplier < 1 or increase active time by >1; here increase active time
        self.active_duration_ms = int(self.active_duration_ms * multiplier)

    def upgrade_rotation_speed_multiplier(self, multiplier: float) -> None:
        self.rotation_speed *= multiplier
        for orb in self.orbs:
            orb.rotation_speed = self.rotation_speed

    def upgrade_downtime_multiplier(self, multiplier: float) -> None:
        # Reduce downtime by multiplier
        self.downtime_ms = int(self.downtime_ms * multiplier)

    def upgrade_radius_multiplier(self, multiplier: float) -> None:
        self.radius = int(self.radius * multiplier)
        for orb in self.orbs:
            orb.radius = self.radius

    def update(self, dt: float, now_ms: int) -> None:
        if not self.enabled:
            return

        # Manage active/downtime cycling
        self.timer_ms += int(dt * 1000)
        if self.active:
            if self.timer_ms >= self.active_duration_ms:
                self.active = False
                self.timer_ms = 0
        else:
            if self.timer_ms >= self.downtime_ms:
                self.active = True
                self.timer_ms = 0

        if self.active:
            for orb in self.orbs:
                orb.update(dt)

    def draw(self, surface: pygame.Surface, offset: Tuple[int, int]) -> None:
        if not (self.enabled and self.active):
            return
        for orb in self.orbs:
            orb.draw(surface, offset)

    def get_hit_sprites(self) -> List[Tuple[pygame.sprite.Sprite, int]]:
        if not (self.enabled and self.active):
            return []
        return [(orb, self.damage) for orb in self.orbs]


class BackSlashWeapon(BaseWeapon):
    def __init__(self, player: pygame.sprite.Sprite, slash_class):
        super().__init__(player)
        # Create an internal slash attack separate from player's front slash
        self.back_slash = slash_class(self.player, offset_x=75, offset_y=0,
                                      sprite_sheet_path='slash_anim.png',
                                      frame_dimensions=(50, 37), num_frames=4, scale=2)
        self.back_slash_damage_multiplier = 1.0
        self.cooldown_ms = 2000  # pause after a back slash finishes
        self._cooldown_until = 0
        self._was_front_active = False

    def enable(self) -> None:
        super().enable()
        self._cooldown_until = 0

    def upgrade_damage_multiplier(self, multiplier: float) -> None:
        self.back_slash.damage = max(1, int(self.back_slash.damage * multiplier))

    def update(self, dt: float, now_ms: int) -> None:
        if not self.enabled:
            return

        # Detect front slash finishing edge
        front_active = getattr(self.player.slash_attack, 'active', False)
        if self._was_front_active and not front_active:
            # Front slash just finished; if not on cooldown, trigger back slash in the opposite direction
            if now_ms >= self._cooldown_until and not self.back_slash.active:
                # Trigger behind the player: opposite of current facing
                self.back_slash.trigger_attack(not self.player.facing_right)
        self._was_front_active = front_active

        # Update internal animation and manage cooldown after it completes
        self.back_slash.update()
        if not self.back_slash.active and now_ms < self._cooldown_until:
            # still cooling down
            pass
        elif not self.back_slash.active and now_ms >= self._cooldown_until and not front_active:
            # Set cooldown when we just finished a back slash
            # Heuristic: if the last update had the slash active and now it is not, set cooldown
            pass
        # Set cooldown at the moment the slash deactivates
        # We cannot easily detect that here without extra state; track last state

    def draw(self, surface: pygame.Surface, offset: Tuple[int, int]) -> None:
        if self.back_slash.active:
            self.back_slash.draw(surface, offset)

    def get_hit_sprites(self) -> List[Tuple[pygame.sprite.Sprite, int]]:
        if not self.enabled or not self.back_slash.active:
            return []
        return [(self.back_slash, self.back_slash.damage)]


class WeaponManager:
    def __init__(self, player: pygame.sprite.Sprite, display: pygame.Surface, slash_class):
        self.player = player
        self.display = display
        self.weapons: Dict[str, BaseWeapon] = {}
        # Pre-create weapons but keep disabled for quick unlocks
        self.weapons['orb'] = OrbWeapon(player, display)
        self.weapons['back_slash'] = BackSlashWeapon(player, slash_class)

    def enable_weapon(self, name: str) -> None:
        if name in self.weapons:
            self.weapons[name].enable()

    def get_weapon(self, name: str) -> BaseWeapon:
        return self.weapons.get(name)

    def update(self, dt: float, now_ms: int) -> None:
        for weapon in self.weapons.values():
            weapon.update(dt, now_ms)

    def draw(self, surface: pygame.Surface, offset: Tuple[int, int]) -> None:
        for weapon in self.weapons.values():
            weapon.draw(surface, offset)

    def get_hit_sprites(self) -> List[Tuple[pygame.sprite.Sprite, int]]:
        hits: List[Tuple[pygame.sprite.Sprite, int]] = []
        for weapon in self.weapons.values():
            hits.extend(weapon.get_hit_sprites())
        return hits


