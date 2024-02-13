import pygame

class Animation:
    def __init__(self, sprite_sheet, animations, sprite_size, scale=1):
        self.sprite_sheet = sprite_sheet
        self.animations = animations  # A dict with names linked to (start_frame, end_frame, frame_rate)
        self.sprite_size = sprite_size  # Size of a single frame
        self.scale = scale
        self.frames = {}  # To store frames for each animation
        self.frame_rates = {}  # Specific frame rates for each animation

        # Calculate the total number of frames based on the sprite sheet's width and the width of a single frame
        total_frames = self.sprite_sheet.get_width() // sprite_size[0]

        for name, (start, end, rate) in animations.items():
            # Here we ensure that the end frame does not exceed the total number of frames
            end = min(end, total_frames - 1)
            self.frames[name] = self.load_frames(0, start, end)  # All animations are in row 0
            self.frame_rates[name] = rate

        self.current_animation = None
        self.current_frames = []
        self.current_frame = 0
        self.current_frame_rate = 100  # Default frame rate
        self.last_update = pygame.time.get_ticks()
        self.set_animation(next(iter(self.animations)))  # Set to the first animation

    def load_frames(self, row, start_frame, end_frame):
        frames = []
        frame_width, frame_height = self.sprite_size
        for frame_num in range(start_frame, end_frame + 1):
            frame_rect = pygame.Rect(frame_num * frame_width, row * frame_height, frame_width, frame_height)
            frame_image = self.sprite_sheet.subsurface(frame_rect).copy()
            frame_image = pygame.transform.scale(frame_image, (int(frame_width * self.scale), int(frame_height * self.scale)))
            frames.append(frame_image)
        return frames

    def set_animation(self, name):
        if name in self.frames and name != self.current_animation:
            self.current_animation = name
            self.current_frames = self.frames[name]
            self.current_frame = 0
            self.current_frame_rate = self.frame_rates[name]

    def update(self):
        now = pygame.time.get_ticks()
        if now - self.last_update > self.current_frame_rate:
            self.last_update = now
            self.current_frame = (self.current_frame + 1) % len(self.current_frames)

    def get_current_frame(self):
        return self.current_frames[self.current_frame]