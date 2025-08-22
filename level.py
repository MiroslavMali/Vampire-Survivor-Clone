import pygame
import random

from player import Player
from enemy_manager import EnemyManager
from scoreboard import Scoreboard
from settings import *
from health_bar import HealthBar
from pause_menu import PauseMenu
from enemy_drop import EnemyDrop
from xp_bar import XPBar
from camera import Camera
from level_up_screen import LevelUpScreen
from upgrade_system import UPGRADE_CHOICES, apply_upgrade, compute_available_upgrades
from weapons import WeaponManager


# --- Floating damage numbers (screen-space overlay) ---
class DamageNumber:
    def __init__(self, text: str, world_pos, font: pygame.font.Font,
                 color=(255, 255, 255), outline=(0, 0, 0), duration_ms=2000):
        # World-space anchor so numbers do not follow the camera
        self.world_x, self.world_y = float(world_pos[0]), float(world_pos[1])
        self.start_world_y = float(self.world_y)
        self.start_time = pygame.time.get_ticks()
        self.duration = duration_ms
        self.alive = True
        self.font = font
        self.base_surface = self._render_with_outline(text, font, color, outline)
        self.scale = 1.0
        self.alpha = 255

    def _render_with_outline(self, text, font, color, outline, thickness=2):
        text_surf = font.render(str(text), True, color).convert_alpha()
        w, h = text_surf.get_size()
        surf = pygame.Surface((w + thickness * 2, h + thickness * 2), pygame.SRCALPHA)
        # Outline by 8-neighborhood
        if thickness > 0:
            outline_surf = font.render(str(text), True, outline).convert_alpha()
            for dx in (-thickness, 0, thickness):
                for dy in (-thickness, 0, thickness):
                    if dx == 0 and dy == 0:
                        continue
                    surf.blit(outline_surf, (dx + thickness, dy + thickness))
        surf.blit(text_surf, (thickness, thickness))
        return surf

    def update(self, now_ms: int):
        if not self.alive:
            return
        elapsed = now_ms - self.start_time
        if elapsed >= self.duration:
            self.alive = False
            return
        t = elapsed / self.duration
        # Hover up ~28 px over lifetime (in world space)
        self.world_y = self.start_world_y - 28.0 * t
        self.scale = 1.0 - 0.35 * t  # shrink to ~65%
        self.alpha = max(0, 255 - int(255 * t))

    def draw(self, surface: pygame.Surface, offset=(0, 0)):
        if not self.alive:
            return
        img = self.base_surface
        if self.scale != 1.0:
            w = max(1, int(img.get_width() * self.scale))
            h = max(1, int(img.get_height() * self.scale))
            img = pygame.transform.smoothscale(img, (w, h))
        img = img.copy()  # isolate alpha per instance to avoid trails
        img.set_alpha(self.alpha)
        screen_x = self.world_x - offset[0]
        screen_y = self.world_y - offset[1]
        surface.blit(img, (int(screen_x - img.get_width() / 2), int(screen_y - img.get_height())))


class DamageNumberManager:
    def __init__(self, display: pygame.Surface):
        self.display = display
        self.font = pygame.font.Font(None, 32)
        self.items: list[DamageNumber] = []

    def spawn(self, value: int, world_pos):
        try:
            dn = DamageNumber(str(value), world_pos, self.font)
            self.items.append(dn)
        except Exception:
            pass

    def update(self, now_ms: int):
        for dn in self.items:
            dn.update(now_ms)
        self.items = [dn for dn in self.items if dn.alive]

    def draw(self, surface: pygame.Surface, offset):
        for dn in self.items:
            dn.draw(surface, offset)


# --- Performance overlay (simple frame/update timing and counts) ---
class PerfOverlay:
    def __init__(self, display: pygame.Surface, clock: pygame.time.Clock):
        self.display = display
        self.clock = clock
        self.t0 = None
        self.update_ms = 0.0
        self.frame_ms = 0.0
        self.hist_frames = []  # last N frame ms
        self.hist_updates = []  # last N update ms
        self.max_hist = 90
        # Bigger font for readability
        self.font = pygame.font.SysFont(None, 22)
        # Throttle UI updates so numbers are readable
        self.display_update_interval_ms = 250
        self._last_display_ticks = 0
        self._cached_surfaces = []
        self._cached_size = (0, 0)

    def start_frame(self):
        import time
        self.t0 = time.perf_counter()
        self.update_ms = 0.0
        self.frame_ms = 0.0

    def mark_update_end(self):
        import time
        if self.t0 is None:
            return
        self.update_ms = (time.perf_counter() - self.t0) * 1000.0

    def end_frame(self):
        import time
        if self.t0 is None:
            return
        self.frame_ms = (time.perf_counter() - self.t0) * 1000.0
        self.hist_frames.append(self.frame_ms)
        self.hist_updates.append(self.update_ms)
        if len(self.hist_frames) > self.max_hist:
            self.hist_frames.pop(0)
        if len(self.hist_updates) > self.max_hist:
            self.hist_updates.pop(0)
        self.t0 = None

    def _avg(self, arr):
        return sum(arr) / len(arr) if arr else 0.0

    def draw(self, num_enemies: int, num_drops: int, num_dmg_numbers: int):
        # Update cached text surfaces at most twice per second
        now_ticks = pygame.time.get_ticks()
        if (now_ticks - self._last_display_ticks >= self.display_update_interval_ms) or not self._cached_surfaces:
            lines = [
                f"FPS: {int(self.clock.get_fps())}",
                f"frame: {self.frame_ms:.1f} ms (avg {self._avg(self.hist_frames):.1f})",
                f"update: {self.update_ms:.1f} ms (avg {self._avg(self.hist_updates):.1f})",
                f"enemies: {num_enemies}  drops: {num_drops}",
                f"dmg nums: {num_dmg_numbers}",
            ]
            padding = 12
            max_w = 0
            h = padding
            surfaces = []
            for txt in lines:
                s = self.font.render(txt, False, (255, 255, 255))
                surfaces.append(s)
                max_w = max(max_w, s.get_width())
                h += s.get_height() + 2
            w = max_w + padding * 2
            h += padding - 2
            self._cached_surfaces = surfaces
            self._cached_size = (w, h)
            self._last_display_ticks = now_ticks
        else:
            padding = 12
            w, h = self._cached_size
            surfaces = self._cached_surfaces
        x = self.display.get_width() - w - 24
        y = 60  # drop down a bit from the top
        # Background
        bg = pygame.Surface((w, h), pygame.SRCALPHA)
        bg.fill((0, 0, 0, 160))
        self.display.blit(bg, (x, y))
        pygame.draw.rect(self.display, (209, 184, 124), (x, y, w, h), 2)
        # Text
        ty = y + padding
        for s in surfaces:
            self.display.blit(s, (x + padding, ty))
            ty += s.get_height() + 2

class Level:
    def __init__(self, display, game_state_manager, clock):
        self.display = display
        self.background_img = pygame.image.load('rock_bg.jpg').convert()
        self.tile_size = self.background_img.get_size()
        self.game_state_manager = game_state_manager
        self.player = Player(self.display)
        self.camera = Camera(self.player, display.get_size())
        self.enemy_manager = EnemyManager(self.display, 20, 20)
        self.scoreboard = Scoreboard(self.display, clock)
        self.health_bar = HealthBar(self.display, self.player)
        self.pause_menu = PauseMenu(self.display, game_state_manager)
        self.drops = pygame.sprite.Group()
        self.xp_bar = XPBar(self.display, self.player)
        self.clock = clock
        self.last_update = pygame.time.get_ticks()
        
        # Level-up system
        self.level_up_screen = LevelUpScreen(self.display)
        self.player_previous_level = self.player.level
        
        # Weapons system
        from slash_attack import SlashAttack
        self.weapons = WeaponManager(self.player, self.display, SlashAttack)
        # Track taken upgrade counts
        self.taken_upgrades = {}

        # Damage numbers overlay
        self.damage_numbers = DamageNumberManager(self.display)
        # Performance overlay
        self.perf = PerfOverlay(self.display, clock)

        # Drop effects dispatcher
        self.drop_effects = {
            'health': self._effect_health,
            'exp': self._effect_exp,
            'magnet': self._effect_magnet,
        }

    def handle_events(self, events):
        for event in events:
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    was_paused = self.pause_menu.is_paused
                    self.pause_menu.is_paused = not self.pause_menu.is_paused
                    # On resume, prevent enemy catch-up
                    if was_paused and not self.pause_menu.is_paused:
                        now = pygame.time.get_ticks()
                        try:
                            for enemy in self.enemy_manager.enemy_list:
                                setattr(enemy, '_last_update_time', now)
                            self.enemy_manager.last_spawn_time = now
                        except Exception:
                            pass
                elif event.key == pygame.K_p:
                    # Debug cheat: add just enough XP to reach next level
                    try:
                        delta = max(1, self.player.xp_to_next_level - self.player.current_xp)
                        self.player.increase_xp(delta)
                    except Exception:
                        pass
            elif event.type == pygame.MOUSEBUTTONDOWN:
                # Handle mouse button down events
                pass

    def check_level_up(self):
        """Check if player leveled up and show upgrade screen."""
        if self.player.level > self.player_previous_level:
            self.player_previous_level = self.player.level
            self.show_level_up_choices()
    
    def show_level_up_choices(self):
        """Show level-up screen with random upgrade choices."""
        # Compute eligible upgrades based on prerequisites and pick limits
        filtered = compute_available_upgrades(self.player, self.weapons, self.taken_upgrades)
        available_upgrades = list(filtered.keys())
        # Randomly select 3 upgrades
        selected_upgrades = random.sample(available_upgrades, min(3, len(available_upgrades)))
        upgrade_choices = [filtered[upgrade] for upgrade in selected_upgrades]
        self.level_up_screen.show_upgrades(upgrade_choices)
    
    def handle_level_up_events(self, events):
        """Handle level-up screen events."""
        if self.level_up_screen.is_active:
            selected_upgrade = self.level_up_screen.handle_events(events)
            if selected_upgrade:
                self.apply_upgrade(selected_upgrade)
    
    def apply_upgrade(self, upgrade):
        """Apply the selected upgrade to the player."""
        effect = upgrade['effect']
        value = upgrade['value']
        apply_upgrade(effect, value, self.player, self.weapons)
        # Prevent enemy catch-up after overlay by resetting their last update time
        now = pygame.time.get_ticks()
        try:
            for enemy in self.enemy_manager.enemy_list:
                setattr(enemy, '_last_update_time', now)
            # Also reset spawn timer so spawns don't burst
            self.enemy_manager.last_spawn_time = now
        except Exception:
            pass
        # Track taken count by key name if present in catalog
        for key, data in UPGRADE_CHOICES.items():
            if data['effect'] == effect and data['value'] == value and data['name'] == upgrade['name']:
                self.taken_upgrades[key] = self.taken_upgrades.get(key, 0) + 1
                break

    def draw_background_with_offset(self, offset):
        offset_x, offset_y = offset

        # Calculate the starting tile position based on the offset
        start_x = offset_x % self.tile_size[0]
        start_y = offset_y % self.tile_size[1]

        # Calculate the number of tiles needed to cover the screen
        tiles_x = int(DISPLAY_WIDTH / self.tile_size[0]) + 2
        tiles_y = int(DISPLAY_HEIGHT / self.tile_size[1]) + 2

        # Draw each tile, adjusted by the current camera offset
        for y in range(tiles_y):
            for x in range(tiles_x):
                tile_pos = (x * self.tile_size[0] - start_x, y * self.tile_size[1] - start_y)
                self.display.blit(self.background_img, tile_pos)

    def check_collisions(self):
        """Handle player/enemy collisions and manage enemy attacks based on cooldown."""
        current_time = pygame.time.get_ticks()
        # Reset stop flags each frame before computing current collisions
        for enemy in self.enemy_manager.enemy_list:
            enemy.stopped_due_to_attack = False

        hits = pygame.sprite.spritecollide(
            self.player,
            self.enemy_manager.enemy_list,
            False,
            collided=pygame.sprite.collide_rect_ratio(0.6)
        )
        for enemy in hits:
            enemy.stopped_due_to_attack = True
            enemy.attack(self.player, current_time)

    def check_slash_collisions(self):
        if self.player.slash_attack.active:
            current_time = pygame.time.get_ticks()
            hits = pygame.sprite.spritecollide(self.player.slash_attack, self.enemy_manager.enemy_list, dokill=False)
            for enemy in hits:
                # Avoid double-counting within a single slash animation
                if getattr(self.player.slash_attack, 'has_hit', None) and self.player.slash_attack.has_hit(enemy):
                    continue
                # Apply damage instead of instant kill
                dmg = self.player.slash_attack.damage
                if enemy.take_damage(dmg, hit_source_pos=self.player.rect.center):  # Enemy died
                    # Death is handled by enemy fade logic
                    
                    # Create drops using enemy's specific drop types and weights
                    if random.random() < enemy.drop_chance:
                        drop_type = EnemyDrop.determine_drop_type(enemy.drop_types, enemy.drop_weights)
                        drop = EnemyDrop(self.display, enemy.rect.center, drop_type, 2)
                        self.drops.add(drop)
                # Spawn floating damage number at enemy world position (rate-limited)
                last_dn = getattr(enemy, 'last_damage_number_ms', 0)
                if current_time - last_dn > 150:
                    world_pos = (enemy.rect.centerx, enemy.rect.centery - 10)
                    self.damage_numbers.spawn(dmg, world_pos)
                    setattr(enemy, 'last_damage_number_ms', current_time)
                # Mark as hit for this slash
                if getattr(self.player.slash_attack, 'mark_hit', None):
                    self.player.slash_attack.mark_hit(enemy)

    

    def check_drop_collisions(self):
        # Visual collect: trigger bounce then return; apply when ready
        drops_hit = pygame.sprite.spritecollide(self.player, self.drops, dokill=False, collided=pygame.sprite.collide_rect_ratio(0.5))
        for drop in drops_hit:
            drop.start_collect(self.player.rect.center)

        # Update collect animations and apply when ready (use frame dt from run loop)
        dt = getattr(self, 'frame_dt', 0.016)
        for drop in list(self.drops):
            if hasattr(drop, 'update_collect'):
                drop.update_collect(self.player.rect, dt)
            if getattr(drop, 'ready_to_apply', False):
                effect_fn = self.drop_effects.get(drop.drop_type)
                if effect_fn:
                    effect_fn(drop)
                drop.kill()

    # --- Drop effect handlers ---
    def _effect_health(self, drop):
        self.player.increase_health(drop.value)

    def _effect_exp(self, drop):
        self.player.increase_xp(drop.value)

    def _effect_magnet(self, drop):
        # Immediate vacuum: force all current drops to return to player
        for d in self.drops:
            if d is drop:
                # Applying this magnet drop itself; continue to other drops
                continue
            if hasattr(d, 'force_return_to_player'):
                d.force_return_to_player(self.player.rect.center)
        # Optional: also activate player magnet power-up timer for future spawns
        self.player.activate_magnet_power_up(5000)

    def update_drops_magnetic_attraction(self):
        """Update all drops with magnetic attraction to player."""
        magnetic_radius = self.player.get_magnetic_radius()
        for drop in self.drops:
            drop.update_magnetic_attraction(self.player.rect, magnetic_radius)

    def reset(self):
        self.player.reset()
        self.enemy_manager.reset()
        self.scoreboard.reset()

    def run(self, events):
        self.handle_events(events)
        now = pygame.time.get_ticks()
        dt = (now - self.last_update) / 1000.0  # Convert milliseconds to seconds for dt
        self.last_update = now
        self.frame_dt = dt
        current_time = now  # Use current_time for updates that don't need dt

        # Handle level-up screen events first
        self.handle_level_up_events(events)

        if not self.pause_menu.is_paused and not self.level_up_screen.is_active:
            # Begin perf timing for this frame
            try:
                self.perf.start_frame()
            except Exception:
                pass
            self.camera.update()
            self.player.update(dt)
            self.player.update_magnet_power_up()  # Update magnet power-up timer

            self.draw_background_with_offset((self.camera.offset_x, self.camera.offset_y))

            offset = (self.camera.offset_x, self.camera.offset_y)

            self.display.blit(self.player.image, self.player.rect.topleft - pygame.math.Vector2(offset))
            
            self.enemy_manager.update(self.player.rect.center, (self.camera.offset_x, self.camera.offset_y), current_time, self.player.level)

            # Weapons update/draw
            self.weapons.update(dt, current_time)
            self.weapons.draw(self.display, offset)

            # Update drops with magnetic attraction
            self.update_drops_magnetic_attraction()
            
            for drop in self.drops:
                drop.draw(self.display, offset)

            if self.player.slash_attack.active:
                self.player.slash_attack.draw(self.display, offset)
            # Draw damage numbers last (world -> screen using camera offset)
            self.damage_numbers.draw(self.display, (self.camera.offset_x, self.camera.offset_y))

            self.check_collisions()
            self.check_slash_collisions()
            # Weapon collisions
            for weapon_sprite, dmg in self.weapons.get_hit_sprites():
                hits = pygame.sprite.spritecollide(weapon_sprite, self.enemy_manager.enemy_list, dokill=False)
                for enemy in hits:
                    # Use player center for knockback anchor
                    if enemy.take_damage(dmg, hit_source_pos=self.player.rect.center):
                        # Do not kill immediately, start death fade handled by enemy
                        if random.random() < enemy.drop_chance:
                            drop_type = EnemyDrop.determine_drop_type(enemy.drop_types, enemy.drop_weights)
                            drop = EnemyDrop(self.display, enemy.rect.center, drop_type, 2)
                            self.drops.add(drop)
                    # Damage number for weapon hit (rate-limited)
                    last_dn = getattr(enemy, 'last_damage_number_ms', 0)
                    if current_time - last_dn > 150:
                        world_pos = (enemy.rect.centerx, enemy.rect.centery - 10)
                        self.damage_numbers.spawn(dmg, world_pos)
                        setattr(enemy, 'last_damage_number_ms', current_time)
            self.check_drop_collisions()
            # Overlay updates
            self.damage_numbers.update(current_time)
            self.scoreboard.update()
            self.health_bar.update(offset)
            self.xp_bar.update(self.player.current_xp, self.player.xp_to_next_level)
            
            # Check for level up after XP update
            self.check_level_up()
            # Finalize perf timing and draw overlay on top
            try:
                self.perf.mark_update_end()
                self.perf.end_frame()
                self.perf.draw(len(self.enemy_manager.enemy_list), len(self.drops), len(self.damage_numbers.items))
            except Exception:
                pass

        elif self.pause_menu.is_paused:
            self.pause_menu.update(events)
            self.pause_menu.draw()
        elif self.level_up_screen.is_active:
            # Draw the current scene without updating gameplay so overlay shows the game behind
            self.draw_background_with_offset((self.camera.offset_x, self.camera.offset_y))
            offset = (self.camera.offset_x, self.camera.offset_y)
            self.display.blit(self.player.image, self.player.rect.topleft - pygame.math.Vector2(offset))
            self.enemy_manager.draw(self.display, offset)
            for drop in self.drops:
                drop.draw(self.display, offset)
            if self.player.slash_attack.active:
                self.player.slash_attack.draw(self.display, offset)
            # Keep numbers visible during overlay (use camera offset)
            self.damage_numbers.draw(self.display, (self.camera.offset_x, self.camera.offset_y))
            self.health_bar.update(offset)
            self.xp_bar.update(self.player.current_xp, self.player.xp_to_next_level)
            try:
                self.scoreboard.draw_score()
            except Exception:
                pass
        
        # Always draw level-up screen if active (on top of everything)
        if self.level_up_screen.is_active:
            self.level_up_screen.draw()