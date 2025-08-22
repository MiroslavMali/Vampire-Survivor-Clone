from typing import Dict, Any

# For compatibility converting legacy per-frame speed upgrades to dt-based
BASE_FRAME_RATE = 90.0

# Centralized upgrade data and application logic

UPGRADE_CHOICES: Dict[str, Dict[str, Any]] = {
    # Slash upgrades (compat with earlier design)
    'slash_damage': {
        'name': 'Sharp Blade',
        'description': 'Increase slash damage by 20%',
        'effect': 'slash_damage_multiplier',
        'value': 1.2,
        'max_picks': 6,
    },
    'slash_speed': {
        'name': 'Quick Strike',
        'description': 'Reduce slash cooldown by 20%',
        'effect': 'slash_cooldown_reduction',
        'value': 0.8,
        'max_picks': 6,
    },
    # Attacks
    'unlock_orb': {
        'name': 'Magic Orb',
        'description': 'Unlock an orb that orbits you and damages enemies',
        'effect': 'unlock_orb',
        'value': 1,
        'max_picks': 1,
    },
    'orb_rotation_speed': {
        'name': 'Orb Spin',
        'description': 'Increase orb rotation speed by 20%',
        'effect': 'orb_rotation_speed_multiplier',
        'value': 1.2,
        'max_picks': 6,
    },
    'orb_count_plus': {
        'name': 'More Orbs',
        'description': '+1 orb (max 5)',
        'effect': 'orb_count_plus',
        'value': 1,
        'max_picks': 4,
    },
    'orb_damage_up': {
        'name': 'Orb Power',
        'description': 'Increase orb damage by 30%',
        'effect': 'orb_damage_multiplier',
        'value': 1.3,
        'max_picks': 8,
    },
    'orb_uptime_up': {
        'name': 'Orb Uptime',
        'description': 'Increase orb uptime by 20%',
        'effect': 'orb_uptime_multiplier',
        'value': 1.2,
        'max_picks': 5,
    },
    'orb_cooldown_up': {
        'name': 'Orb Cooldown',
        'description': 'Reduce orb downtime by 20%',
        'effect': 'orb_downtime_multiplier',
        'value': 0.8,
        'max_picks': 6,
    },
    'orb_range_up': {
        'name': 'Orb Range',
        'description': 'Increase orb range by 20%',
        'effect': 'orb_radius_multiplier',
        'value': 1.2,
        'max_picks': 8,
    },

    'unlock_back_slash': {
        'name': 'Back Slash',
        'description': 'Slash behind you after the front slash',
        'effect': 'unlock_back_slash',
        'value': 1,
        'max_picks': 1,
    },
    'back_slash_damage_up': {
        'name': 'Back Slash Power',
        'description': 'Increase back slash damage by 30%',
        'effect': 'slash_back_damage_multiplier',
        'value': 1.3,
        'max_picks': 8,
    },

    # Stats
    'speed_boost': {
        'name': 'Swift Feet',
        'description': 'Increase movement speed by 20%',
        'effect': 'move_speed_plus',
        'value': 1.2,
        'max_picks': 10,
    },
    'pickup_boost': {
        'name': 'Magnetic Field',
        'description': 'Increase pickup range by 25%',
        'effect': 'pickup_radius_plus',
        'value': 25,
        'max_picks': 10,
    },
    'health_boost': {
        'name': 'Vitality',
        'description': 'Increase max health by 20',
        'effect': 'max_health_plus',
        'value': 20,
        'max_picks': 10,
    },
    'xp_boost': {
        'name': 'Experience',
        'description': 'Gain 20% more XP',
        'effect': 'xp_multiplier',
        'value': 1.2,
        'max_picks': 8,
    },
}


def apply_upgrade(effect: str, value, player, weapons) -> None:
    """Apply an upgrade effect to player or weapons."""
    # Backward compatibility: legacy 'unlock_attack' with value 'orb'
    if effect == 'unlock_attack' and value == 'orb':
        effect = 'unlock_orb'

    if effect == 'unlock_orb':
        weapons.enable_weapon('orb')
    elif effect == 'orb_count_plus':
        weapons.get_weapon('orb').upgrade_count(value)
    elif effect == 'orb_damage_multiplier':
        weapons.get_weapon('orb').upgrade_damage_multiplier(value)
    elif effect == 'orb_uptime_multiplier':
        weapons.get_weapon('orb').upgrade_uptime_multiplier(value)
    elif effect == 'orb_rotation_speed_multiplier':
        weapons.get_weapon('orb').upgrade_rotation_speed_multiplier(value)
    elif effect == 'orb_downtime_multiplier':
        weapons.get_weapon('orb').upgrade_downtime_multiplier(value)
    elif effect == 'orb_radius_multiplier':
        weapons.get_weapon('orb').upgrade_radius_multiplier(value)

    elif effect == 'unlock_back_slash':
        weapons.enable_weapon('back_slash')
    elif effect == 'slash_back_damage_multiplier':
        weapons.get_weapon('back_slash').upgrade_damage_multiplier(value)

    # Core slash (front) upgrades
    elif effect == 'slash_damage_multiplier':
        try:
            player.slash_attack.damage = max(1, int(player.slash_attack.damage * value))
        except Exception:
            pass
    elif effect == 'slash_cooldown_reduction':
        try:
            # Reduce by multiplier but keep a minimum cooldown
            new_cd = int(player.slash_cooldown * value)
            player.slash_cooldown = max(200, new_cd)
        except Exception:
            pass

    elif effect == 'move_speed_plus':
        # Convert flat value into a percentage of current base speed (treat 0.4 as 20%)
        if hasattr(player, 'speed'):
            player.speed *= 1.2
    elif effect == 'pickup_radius_plus':
        # Percent of original base (store once), value is percent (e.g., 25)
        if not hasattr(player, '_magnet_base'):
            player._magnet_base = getattr(player, 'magnetic_radius', 50)
        player.magnetic_radius += int(player._magnet_base * (value / 100.0))
    elif effect == 'max_health_plus':
        player.max_health += value
        player.current_health += value
    elif effect == 'xp_multiplier':
        if not hasattr(player, 'xp_multiplier'):
            player.xp_multiplier = 1.0
        player.xp_multiplier *= value


def compute_available_upgrades(player, weapons, taken_counts: Dict[str, int]) -> Dict[str, Dict[str, Any]]:
    """Filter upgrades by prerequisites and max pick limits.

    Rules:
    - Unlocks (e.g., unlock_orb/back_slash) are shown only if not already enabled.
    - Weapon upgrades (orb_*, back_slash_*) require the weapon to be enabled.
    - Respect 'max_picks' counts stored in taken_counts by key.
    """
    available: Dict[str, Dict[str, Any]] = {}

    def is_weapon_enabled(name: str) -> bool:
        w = weapons.get_weapon(name)
        return bool(w and getattr(w, 'enabled', False))

    for key, data in UPGRADE_CHOICES.items():
        max_picks = data.get('max_picks')
        taken = taken_counts.get(key, 0)
        if max_picks is not None and taken >= max_picks:
            continue

        # Weapon pre-reqs
        if key.startswith('orb_') and key != 'unlock_orb':
            if not is_weapon_enabled('orb'):
                continue
        if key.startswith('back_slash') and key != 'unlock_back_slash':
            if not is_weapon_enabled('back_slash'):
                continue

        # Unlocks only if not already enabled
        if key == 'unlock_orb' and is_weapon_enabled('orb'):
            continue
        if key == 'unlock_back_slash' and is_weapon_enabled('back_slash'):
            continue

        available[key] = data

    return available


