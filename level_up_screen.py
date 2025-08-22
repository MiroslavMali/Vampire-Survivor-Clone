import pygame
from settings import *


class LevelUpScreen:
    def __init__(self, display):
        self.display = display
        self.is_active = False
        self.upgrade_choices = []
        self.selected_choice = None

        # Window (narrower, centered)
        self.window_width = 520
        self.window_height = 520
        self.window_x = (DISPLAY_WIDTH // 2) - (self.window_width // 2)
        self.window_y = (DISPLAY_HEIGHT // 2) - (self.window_height // 2)

        # Vertical card layout
        self.card_margin_h = 24
        self.card_margin_v = 24
        self.card_spacing = 14
        self.card_height = 110
        self.icon_size = 56
        self.icon_pad = 14
        self.choice_rects = []

        # Colors
        self.overlay_color = (0, 0, 0, 160)
        self.window_color = (54, 62, 90)
        self.window_border_color = (209, 184, 124)
        self.card_color = (80, 80, 88)
        self.card_selected_color = (104, 104, 116)
        self.card_border_color = (209, 184, 124)
        self.text_color = (230, 230, 230)
        self.accent_text_color = (255, 226, 120)
        self.key_text_color = (200, 200, 200)

        # Fonts
        self.title_font = pygame.font.Font(None, 56)
        self.name_font = pygame.font.Font(None, 32)
        self.desc_font = pygame.font.Font(None, 24)

        # Confirm button
        self.confirm_button_width = 160
        self.confirm_button_height = 44
        self.confirm_button_x = self.window_x + (self.window_width - self.confirm_button_width) // 2
        self.confirm_button_y = self.window_y + self.window_height - 60
        self.confirm_button_color = (60, 120, 60)
        self.confirm_button_hover_color = (80, 160, 80)

        # Local icon cache
        self._icon_cache = {}
        # Particles
        self._exp_rain = None
        self._last_tick = pygame.time.get_ticks()

    def show_upgrades(self, upgrade_choices):
        """Show the level-up screen with up to 3 vertical cards."""
        self.is_active = True
        self.upgrade_choices = upgrade_choices[:3]
        self.selected_choice = 0 if self.upgrade_choices else None
        self._rebuild_choice_rects()
        # Start exp rain effect
        self._last_tick = pygame.time.get_ticks()
        self._exp_rain = ExpRain(self.display, initial_count=320, max_count=520,
                                  spawn_rate_per_sec=140, sprite_path='emerald.png',
                                  base_scale=1.5, shrink_speed_multiplier=1.2)

    def _rebuild_choice_rects(self):
        self.choice_rects = []
        inner_w = self.window_width - (self.card_margin_h * 2)
        start_y = self.window_y + 90
        for i in range(len(self.upgrade_choices)):
            y = start_y + i * (self.card_height + self.card_spacing)
            rect = pygame.Rect(self.window_x + self.card_margin_h, y, inner_w, self.card_height)
            self.choice_rects.append(rect)

    def _wrap_text(self, text, max_width, font):
        words = text.split()
        lines = []
        current = ""
        for w in words:
            test = (current + " " + w).strip()
            if font.size(test)[0] <= max_width:
                current = test
            else:
                if current:
                    lines.append(current)
                current = w
        if current:
            lines.append(current)
        return lines[:3]

    def _load_icon(self, path):
        surf = self._icon_cache.get(path)
        if surf is None:
            try:
                surf = pygame.image.load(path).convert_alpha()
            except Exception:
                surf = pygame.image.load('emerald.png').convert_alpha()
            self._icon_cache[path] = surf
        return surf

    def _icon_for_choice(self, choice):
        # Placeholder mapping; default to emerald
        name = (choice.get('name') or '').lower()
        effect = (choice.get('effect') or '').lower()
        path = 'emerald.png'
        if 'health' in name or 'vitality' in name:
            path = 'red_potion.png'
        elif 'magnet' in name or 'pickup' in effect:
            path = 'magnet.png'
        elif 'orb' in name or 'orb' in effect:
            path = 'Orb.png'
        elif 'slash' in name:
            path = 'slash_anim.png'
        return self._load_icon(path)

    def handle_events(self, events):
        if not self.is_active:
            return None

        for event in events:
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for i, rect in enumerate(self.choice_rects):
                    if rect.collidepoint(mouse_pos):
                        self.selected_choice = i
                        break
                confirm_rect = pygame.Rect(self.confirm_button_x, self.confirm_button_y,
                                           self.confirm_button_width, self.confirm_button_height)
                if confirm_rect.collidepoint(mouse_pos) and self.selected_choice is not None:
                    return self.apply_upgrade()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1 and len(self.upgrade_choices) >= 1:
                    self.selected_choice = 0
                elif event.key == pygame.K_2 and len(self.upgrade_choices) >= 2:
                    self.selected_choice = 1
                elif event.key == pygame.K_3 and len(self.upgrade_choices) >= 3:
                    self.selected_choice = 2
                elif event.key in (pygame.K_UP, pygame.K_w):
                    if self.upgrade_choices:
                        self.selected_choice = (0 if self.selected_choice is None
                                                else (self.selected_choice - 1) % len(self.upgrade_choices))
                elif event.key in (pygame.K_DOWN, pygame.K_s):
                    if self.upgrade_choices:
                        self.selected_choice = (0 if self.selected_choice is None
                                                else (self.selected_choice + 1) % len(self.upgrade_choices))
                elif event.key == pygame.K_RETURN and self.selected_choice is not None:
                    return self.apply_upgrade()
        return None

    def apply_upgrade(self):
        if self.selected_choice is not None and self.selected_choice < len(self.upgrade_choices):
            selected_upgrade = self.upgrade_choices[self.selected_choice]
            self.is_active = False
            self.selected_choice = None
            # Stop particles
            self._exp_rain = None
            return selected_upgrade
        return None

    def draw(self):
        if not self.is_active:
            return

        # Dim overlay
        overlay = pygame.Surface((DISPLAY_WIDTH, DISPLAY_HEIGHT))
        overlay.set_alpha(self.overlay_color[3])
        overlay.fill((self.overlay_color[0], self.overlay_color[1], self.overlay_color[2]))
        self.display.blit(overlay, (0, 0))

        # Update and draw particle rain (above overlay, behind window)
        now = pygame.time.get_ticks()
        dt = max(0.0, (now - self._last_tick) / 1000.0)
        dt = min(dt, 0.05)
        self._last_tick = now
        if self._exp_rain:
            self._exp_rain.update(dt)
            self._exp_rain.draw(self.display)

        # Window
        window_rect = pygame.Rect(self.window_x, self.window_y, self.window_width, self.window_height)
        pygame.draw.rect(self.display, self.window_color, window_rect)
        pygame.draw.rect(self.display, self.window_border_color, window_rect, 4)

        # Title
        title_text = self.title_font.render("LEVEL UP!", True, self.accent_text_color)
        title_rect = title_text.get_rect(center=(self.window_x + self.window_width // 2, self.window_y + 40))
        self.display.blit(title_text, title_rect)

        # Cards
        self._rebuild_choice_rects()
        for i, choice in enumerate(self.upgrade_choices):
            rect = self.choice_rects[i]
            color = self.card_selected_color if i == self.selected_choice else self.card_color
            pygame.draw.rect(self.display, color, rect)
            pygame.draw.rect(self.display, self.card_border_color, rect, 3)

            # Icon box
            icon = self._icon_for_choice(choice)
            icon_scaled = pygame.transform.smoothscale(icon, (self.icon_size, self.icon_size))
            icon_x = rect.x + self.icon_pad
            icon_y = rect.y + (rect.height - self.icon_size) // 2
            self.display.blit(icon_scaled, (icon_x, icon_y))

            # Texts
            name = str(choice.get('name', 'Upgrade'))
            # Build description directly from upgrade data (name + effect/value)
            desc = str(choice.get('description', ''))
            name_surf = self.name_font.render(name, True, self.accent_text_color)
            self.display.blit(name_surf, (icon_x + self.icon_size + 14, rect.y + 14))

            # Wrap description
            max_desc_w = rect.width - (self.icon_pad * 2 + self.icon_size + 14)
            lines = self._wrap_text(desc, max_desc_w, self.desc_font)
            for li, line in enumerate(lines):
                line_surf = self.desc_font.render(line, True, self.text_color)
                self.display.blit(line_surf, (icon_x + self.icon_size + 14, rect.y + 44 + li * 22))

            # Key indicator (1..3)
            key_surf = self.desc_font.render(str(i + 1), True, self.key_text_color)
            self.display.blit(key_surf, (rect.right - 24, rect.y + 10))

        # Confirm button
        mouse_pos = pygame.mouse.get_pos()
        confirm_rect = pygame.Rect(self.confirm_button_x, self.confirm_button_y,
                                   self.confirm_button_width, self.confirm_button_height)
        btn_color = self.confirm_button_hover_color if (confirm_rect.collidepoint(mouse_pos) and self.selected_choice is not None) else self.confirm_button_color
        pygame.draw.rect(self.display, btn_color, confirm_rect)
        pygame.draw.rect(self.display, self.window_border_color, confirm_rect, 2)
        confirm_text = self.name_font.render("Confirm", True, self.text_color)
        self.display.blit(confirm_text, confirm_rect.move((confirm_rect.width - confirm_text.get_width()) // 2,
                                                         (confirm_rect.height - confirm_text.get_height()) // 2).topleft)


# --- Level Up Particle Effect: Exp Rain ---
class ExpRain:
    def __init__(self, display, initial_count=300, max_count=500,
                 spawn_rate_per_sec=120, sprite_path='emerald.png',
                 base_scale=1.0, shrink_speed_multiplier=1.0):
        self.display = display
        self.max_count = max_count
        self.spawn_rate_per_sec = spawn_rate_per_sec
        self._spawn_accum = 0.0
        self.particles = []  # list of [x, y, vy, scale_index, shrink_per_sec]
        self._base = self._load_sprite(sprite_path)
        # Precompute scaled variants to avoid per-frame scaling
        # Start bigger (base_scale) and decay until ~0.2
        self._scales = []
        scale = max(0.2, float(base_scale))
        while scale >= 0.2:
            self._scales.append(scale)
            scale *= 0.92  # shrink step per index
        self._scaled_surfaces = [pygame.transform.smoothscale(self._base, (max(1, int(self._base.get_width()*s)),
                                                                           max(1, int(self._base.get_height()*s))))
                                 for s in self._scales]
        # Shrink multiplier must be set before seeding
        self._shrink_mult = float(shrink_speed_multiplier)
        # Seed initial burst
        for _ in range(initial_count):
            self._spawn_one(random_x=True, random_y_above=True)

    def _load_sprite(self, path):
        try:
            return pygame.image.load(path).convert_alpha()
        except Exception:
            return pygame.image.load('emerald.png').convert_alpha()

    def _spawn_one(self, random_x=False, random_y_above=False):
        import random
        x = random.randint(0, DISPLAY_WIDTH - 1) if random_x else 0
        if random_y_above:
            y = -random.uniform(0, DISPLAY_HEIGHT * 1.5)
        else:
            y = -random.uniform(40, 200)  # spawn offscreen
        vy = random.uniform(120.0, 240.0)  # px/sec
        scale_index = 0  # start at full size
        shrink_per_sec = random.uniform(0.8, 1.4) * self._shrink_mult  # faster shrink
        self.particles.append([float(x), float(y), vy, float(scale_index), shrink_per_sec])

    def update(self, dt: float):
        # Spawn continuously up to max_count
        if len(self.particles) < self.max_count:
            self._spawn_accum += dt * self.spawn_rate_per_sec
            while self._spawn_accum >= 1.0 and len(self.particles) < self.max_count:
                self._spawn_one(random_x=True)
                self._spawn_accum -= 1.0

        # Update positions and shrink
        height = DISPLAY_HEIGHT
        alive = []
        for x, y, vy, sidx, shrink in self.particles:
            y += vy * dt
            sidx += shrink * dt
            # Extra shrink near bottom for a fade-out effect
            if y > height * 0.85:
                sidx += 2.0 * dt
            if y < height + 40 and sidx < len(self._scales) - 1:
                alive.append([x, y, vy, sidx, shrink])
        self.particles = alive

    def draw(self, surface):
        # Draw with precomputed scaled surfaces, no per-frame transforms
        for x, y, vy, sidx, shrink in self.particles:
            idx = int(sidx)
            idx = max(0, min(idx, len(self._scaled_surfaces) - 1))
            img = self._scaled_surfaces[idx]
            surface.blit(img, (int(x), int(y)))
