# Enhanced Enemy Configuration System
# All enemy data is centralized here for easy modification

# Attack types and their properties
ATTACK_TYPES = {
    'slash': {
        'damage': 15,
        'cooldown': 1250,
        'range': 75
    },
    'orb': {
        'damage': 10,
        'cooldown': 0,  # Continuous damage
        'range': 100
    }
}

# Drop types and their properties
DROP_TYPES = {
    'health': {
        'sprite': 'red_potion.png',
        'value': 10,
        'weight': 0.3
    },
    'exp': {
        'sprite': 'emerald.png',
        'value': 15,
        'weight': 0.5
    },
    'money': {
        'sprite': 'money_drop.png',
        'value': 5,
        'weight': 0.2
    },
    'magnet': {
        'sprite': 'magnet.png',
        'value': 1,
        'weight': 0.1  # a bit rarer than potion
    }
}

# Global default drop configuration
DEFAULT_DROP = {
    'chance': 0.52,  # Overall chance to drop anything
    # Conditional weights given a drop happens (sum to 1.0)
    # Chosen so marginal chances are: exp 50%, health 1%, magnet 1%
    'weights': {
        'exp': 0.961538,
        'health': 0.019231,
        'magnet': 0.019231,
    },
}

# Enemy type configurations
# Note: speed values are in pixels/second (px/s)
ENEMY_TYPES = {
    'rat': {
        'sprite': 'Rat.png',
        'health': 10,
        'damage': 1,
        'speed': 45,
        'attack_cooldown': 100,
        'xp_value': 5,
        'description': 'Basic enemy, instant kill'
        # Overrides example:
        # 'drop_chance': 0.6,
        # 'drop_types': ['exp', 'health', 'magnet'],
        # 'drop_weights': {'exp': 0.8, 'health': 0.15, 'magnet': 0.05},
    },
    'zombie': {
        'sprite': 'Zombie.png',
        'health': 10,  # Lower health so it dies instantly (no red square)
        'damage': 2,
        'speed': 27,
        'attack_cooldown': 120,
        'xp_value': 8,
        'description': 'Zombie, instant kill, rare health drops'
        # Overrides example:
        # 'drop_chance': 0.4,
        # 'drop_weights': {'exp': 0.6, 'health': 0.3, 'magnet': 0.1},
    },
    'skeleton': {
        'sprite': 'Skeleton.png',
        'health': 25,  # Takes 2 hits to kill (will show damage flash)
        'damage': 3,
        'speed': 36,
        'attack_cooldown': 150,
        'xp_value': 15,
        'description': 'Tough skeleton, takes multiple hits'
        # Overrides example:
        # 'drop_chance': 0.7,
        # 'drop_weights': {'exp': 0.5, 'health': 0.35, 'magnet': 0.15},
    },
    'ghost': {
        'sprite': 'Ghost.png',
        'health': 18,  # Takes 2 hits to kill (will show damage flash)
        'damage': 2,
        'speed': 63,  # Faster than other enemies
        'attack_cooldown': 100,
        'xp_value': 12,
        'description': 'Fast ghost, takes multiple hits'
        # Overrides example:
        # 'drop_chance': 0.55,
        # 'drop_weights': {'exp': 0.65, 'health': 0.25, 'magnet': 0.10},
    }
}

# Spawn weights for different enemy types
ENEMY_SPAWN_WEIGHTS = {
    'rat': 50,        # 50% chance (reduced from 70%)
    'zombie': 25,     # 25% chance (reduced from 30%)
    'skeleton': 15,   # 15% chance
    'ghost': 10       # 10% chance
}

# Level-based enemy unlocks
LEVEL_UNLOCKS = {
    1: ['rat', 'zombie'],
    3: ['rat', 'zombie', 'skeleton'],
    5: ['rat', 'zombie', 'skeleton', 'ghost']
}

# Game balance settings
GAME_BALANCE = {
    'player_starting_health': 100,
    'player_starting_speed': 2,
    'xp_to_next_level_base': 100,
    'level_up_percentage': 100
}
