"""Game constants module."""

import pygame

# Display settings
WIDTH = 800
HEIGHT = 600
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
CYAN = (0, 255, 255)
MAGENTA = (255, 0, 255)

# Player settings
SHIP_SIZE = 20
PLAYER_ACCELERATION = 0.5
PLAYER_MAX_SPEED = 10
PLAYER_FRICTION = 0.98
PLAYER_ROTATION_SPEED = 5
PLAYER_INVULNERABLE_TIME = 180  # 3 seconds at 60 FPS
PLAYER_SHIELD_RADIUS = 30
PLAYER_SHOOT_DELAY = 15  # 0.25 seconds at 60 FPS

# Bullet settings
BULLET_SIZE = 4
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 7  # Slightly slower than player bullets
BULLET_LIFETIME = 60  # 1 second at 60 FPS

# Asteroid settings
ASTEROID_SIZES = {
    'large': 40,
    'medium': 20,
    'small': 10
}
ASTEROID_SPEED_MIN = 1
ASTEROID_SPEED_MAX = 3
ASTEROID_SPIN_MIN = -3
ASTEROID_SPIN_MAX = 3
ASTEROID_VERTICES_MIN = 8
ASTEROID_VERTICES_MAX = 12
ASTEROID_SPAWN_DISTANCE = 100  # Minimum distance from player

# Enemy settings
ENEMY_SPAWN_TIME_MIN = 300  # 5 seconds at 60 FPS
ENEMY_SPAWN_TIME_MAX = 600  # 10 seconds at 60 FPS
ENEMY_SPEED = 3
ENEMY_HEALTH = 2
ENEMY_SHOOT_DELAY_MIN = 30  # 0.5 seconds at 60 FPS
ENEMY_SHOOT_DELAY_MAX = 90  # 1.5 seconds at 60 FPS

# Powerup settings
POWERUP_SIZE = 20
POWERUP_SPEED = 1
POWERUP_DURATION = 600  # 10 seconds at 60 FPS
POWERUP_SPAWN_CHANCE = 0.3  # 30% chance to spawn from destroyed asteroids/enemies
POWERUP_PULSE_SPEED = 0.01
POWERUP_PULSE_RANGE = 4
POWERUP_COLORS = {
    'shield': BLUE,
    'spread_shot': GREEN,
    'rapid_fire': YELLOW,
    'invincibility': MAGENTA
}

# Explosion settings
EXPLOSION_DURATION = 60  # 1 second at 60 FPS
EXPLOSION_PARTICLE_COUNT = 20
EXPLOSION_PARTICLE_SPEED = 5
EXPLOSION_PARTICLE_SIZE = 3
EXPLOSION_COLORS = [
    (255, 200, 50),  # Orange
    (255, 150, 50),  # Dark orange
    (255, 100, 50),  # Red-orange
    (255, 50, 50),   # Red
]

# Game settings
STARTING_LIVES = 3
STARTING_ASTEROIDS = 4

# Debug keys
DEBUG_KEYS = {
    'TOGGLE_INVINCIBLE': pygame.K_F4,
    'SKIP_LEVEL': pygame.K_F5,
    'TOGGLE_SPREAD_SHOT': pygame.K_F9,
    'ADD_SHIELD': pygame.K_F10
}

# Score values
SCORE_VALUES = {
    'asteroid_large': 20,
    'asteroid_medium': 50,
    'asteroid_small': 100,
    'level_complete': 1000
}

# Game object sizes
POWERUP_SPAWN_COOLDOWN = 1800  # 30 seconds at 60 FPS
ENEMY_SPAWN_DELAY = 300  # 5 seconds at 60 FPS
INVULNERABILITY_DURATION = 180  # 3 seconds at 60 FPS
LEVEL_TRANSITION_TIME = 180  # 3 seconds at 60 FPS

# Sound configuration
SOUND_FILES = {
    'thrust': 'thrusterFire_000.ogg',
    'shoot': 'laserSmall_000.ogg',
    'enemy_shoot': 'laserSmall_001.ogg',
    'explosion_small': 'explosionCrunch_000.ogg',
    'explosion_medium': 'explosionCrunch_001.ogg',
    'explosion_large': 'explosionCrunch_002.ogg',
    'powerup': 'laserRetro_003.ogg',
    'shield_hit': 'forceField_000.ogg',
    'level_complete': 'laserLarge_003.ogg',
    'game_over': 'lowFrequency_explosion_000.ogg'
}

SOUND_VOLUMES = {
    'thrust': 0.3,
    'default': 0.7
} 