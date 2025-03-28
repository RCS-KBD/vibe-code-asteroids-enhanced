"""Bullet module."""

import math
import pygame
from src.utils.constants import (
    WIDTH, HEIGHT, WHITE, RED,
    BULLET_SPEED, ENEMY_BULLET_SPEED,
    BULLET_SIZE, BULLET_LIFETIME
)

class Bullet:
    """Bullet class representing projectiles fired by the player or enemies."""

    def __init__(self, position, angle, is_enemy=False):
        """Initialize the bullet.
        
        Args:
            position: Starting position [x, y]
            angle: Direction in degrees (0 is up) or radians (if is_enemy)
            is_enemy: Whether this is an enemy bullet
        """
        self.position = [float(position[0]), float(position[1])]
        self.is_enemy = is_enemy
        
        # Calculate velocity based on angle
        if is_enemy:
            # Enemy bullets use radians and direct angle
            self.velocity = [
                math.cos(angle) * ENEMY_BULLET_SPEED,
                math.sin(angle) * ENEMY_BULLET_SPEED
            ]
        else:
            # Player bullets use degrees and -90 offset (0 is up)
            angle_rad = math.radians(angle - 90)
            self.velocity = [
                math.cos(angle_rad) * BULLET_SPEED,
                math.sin(angle_rad) * BULLET_SPEED
            ]
        
        # Create collision rectangle
        self.rect = pygame.Rect(
            position[0] - BULLET_SIZE // 2,
            position[1] - BULLET_SIZE // 2,
            BULLET_SIZE,
            BULLET_SIZE
        )
        
        # Set lifetime
        self.lifetime = BULLET_LIFETIME

    def update(self):
        """Update bullet position and lifetime."""
        # Update position
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        
        # Wrap around screen edges
        self.position[0] = self.position[0] % WIDTH
        self.position[1] = self.position[1] % HEIGHT
        
        # Update collision rectangle
        self.rect.center = self.position
        
        # Update lifetime
        self.lifetime -= 1

    def draw(self, screen):
        """Draw the bullet."""
        pygame.draw.circle(
            screen,
            RED if self.is_enemy else WHITE,
            [int(self.position[0]), int(self.position[1])],
            BULLET_SIZE // 2
        ) 