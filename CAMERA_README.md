# SmartCamera

A **super easy-to-use** camera system for Pygame games.

`SmartCamera` follows your player smoothly, supports optional camera shake, and can be clamped to your world boundaries.  
Perfect for beginners who want a working camera in **minutes**.

---

## Installation

```bash
pip install smartcamera
```

---

## Quick Start

### 1. Import and create the camera
```python
import pygame
from smartcamera import SmartCamera

pygame.init()
screen = pygame.display.set_mode((800, 600))

# Example player object with a rect
player = pygame.sprite.Sprite()
player.image = pygame.Surface((50, 50))
player.image.fill((255, 0, 0))
player.rect = player.image.get_rect(center=(400, 300))

# Create the camera
camera = SmartCamera(player, (800, 600))
```

---

### 2. Use in your game loop
```python
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000  # Seconds since last frame

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Move player with arrow keys
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        player.rect.x -= 5
    if keys[pygame.K_RIGHT]:
        player.rect.x += 5
    if keys[pygame.K_UP]:
        player.rect.y -= 5
    if keys[pygame.K_DOWN]:
        player.rect.y += 5

    # Update camera
    camera.update(dt)

    # Draw background
    screen.fill((30, 30, 30))

    # Draw player with camera applied
    screen.blit(player.image, camera.apply(player))

    pygame.display.flip()

pygame.quit()
```

---

## Features

### Smooth Follow
- By default, the camera **lerps** (smoothly moves) toward the player.
- Change smoothness:
```python
camera.set_smoothness(0.05)  # Very smooth (slow follow)
camera.set_smoothness(0.3)   # Less smooth (snappier)
```

- Toggle smoothing on/off:
```python
camera.toggle_smooth()
```

---

### Instant Follow
Pass `auto_smooth=False` when creating the camera:
```python
camera = SmartCamera(player, (800, 600), auto_smooth=False)
```

---

### Camera Shake
Shake is great for explosions, hits, or dramatic moments:
```python
camera.add_shake(intensity=10, duration=15)
```
- **intensity** → shake range in pixels  
- **duration** → frames to shake (60 = 1 second at 60 FPS)

---

### World Bounds
Prevent the camera from showing outside your map:
```python
world_rect = pygame.Rect(0, 0, 2000, 2000)  # Map size
camera = SmartCamera(player, (800, 600), world_rect=world_rect)
```

---

### Get Current Offset
You can retrieve the camera's current offset (including shake):
```python
ox, oy = camera.get_offset()
```

---

### Reset Camera
Instantly snap back to the player:
```python
camera.reset()
```

---

## Tips for Beginners

1. **Your player must have a `.rect`** (usually `pygame.Rect`) with correct position.
2. Call `camera.update()` **every frame** before drawing.
3. Use `camera.apply()` when blitting **every moving object**.
4. Static UI (like health bars) should be drawn **without** the camera offset.

---

## Full Example with Multiple Sprites

```python
# Example game objects
enemy = pygame.sprite.Sprite()
enemy.image = pygame.Surface((50, 50))
enemy.image.fill((0, 255, 0))
enemy.rect = enemy.image.get_rect(center=(1000, 800))

# In your draw loop
for entity in [player, enemy]:
    screen.blit(entity.image, camera.apply(entity))
```

---

## License

MIT License © 2025 Your Name
