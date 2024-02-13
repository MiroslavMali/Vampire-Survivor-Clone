class Camera:
    def __init__(self, player, display_size):
        self.player = player
        self.offset_x = 0
        self.offset_y = 0
        self.display_width, self.display_height = display_size

    def update(self):
        self.offset_x = self.player.rect.x - self.display_width // 2
        self.offset_y = self.player.rect.y - self.display_height // 2

    def apply(self, entity):
        # Apply the offset to the entity's position
        return entity.rect.move(-self.offset_x, -self.offset_y)
