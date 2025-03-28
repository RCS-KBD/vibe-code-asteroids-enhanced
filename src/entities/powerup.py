"""Powerup entity module."""

import pygame
from pygame import Vector2
import random
import math
from enum import Enum
from src.utils.constants import (
    WIDTH, HEIGHT,
    POWERUP_SIZE, POWERUP_SPEED,
    POWERUP_DURATION, POWERUP_COLORS,
    POWERUP_PULSE_SPEED, POWERUP_PULSE_RANGE
)

class PowerupType(Enum):
    """Types of powerups available in the game."""
    SHIELD = 'shield'
    SPREAD_SHOT = 'spread_shot'
    RAPID_FIRE = 'rapid_fire'
    INVINCIBILITY = 'invincibility'

class Powerup:
    """Powerup class representing collectible power-ups."""

    def __init__(self, x: float, y: float, powerup_type: str):
        """Initialize the powerup.
        
        Args:
            x: Initial x position
            y: Initial y position
            powerup_type: Type of powerup ('shield' or 'spread_shot')
        """
        self.position = [float(x), float(y)]
        self.type = powerup_type
        self.color = POWERUP_COLORS[powerup_type]
        
        # Movement
        self.angle = 0
        self.speed = POWERUP_SPEED
        
        # Visual effects
        self.pulse = 0
        self.pulse_direction = 1
        
        # Create collision rectangle
        self.rect = pygame.Rect(
            x - POWERUP_SIZE // 2,
            y - POWERUP_SIZE // 2,
            POWERUP_SIZE,
            POWERUP_SIZE
        )
        
        # Set lifetime
        self.lifetime = POWERUP_DURATION

    def update(self):
        """Update powerup position and effects."""
        # Update position (circular motion)
        self.angle = (self.angle + self.speed) % 360
        offset_x = math.cos(math.radians(self.angle)) * 2
        offset_y = math.sin(math.radians(self.angle)) * 2
        
        self.position[0] += offset_x
        self.position[1] += offset_y
        
        # Wrap around screen edges
        self.position[0] = self.position[0] % WIDTH
        self.position[1] = self.position[1] % HEIGHT
        
        # Update collision rectangle
        self.rect.center = self.position
        
        # Update pulse effect
        self.pulse += POWERUP_PULSE_SPEED * self.pulse_direction
        if self.pulse >= 1:
            self.pulse = 1
            self.pulse_direction = -1
        elif self.pulse <= 0:
            self.pulse = 0
            self.pulse_direction = 1
        
        # Update lifetime
        self.lifetime -= 1

    def draw(self, screen):
        """Draw the powerup."""
        # Calculate pulse size
        size = POWERUP_SIZE + int(self.pulse * POWERUP_PULSE_RANGE)
        
        # Draw outer circle
        pygame.draw.circle(
            screen,
            self.color,
            [int(self.position[0]), int(self.position[1])],
            size,
            2
        )
        
        # Draw inner shape based on type
        if self.type == 'shield':
            # Draw shield symbol (three arcs)
            for i in range(3):
                angle = i * 120 + self.angle
                start_angle = math.radians(angle - 30)
                end_angle = math.radians(angle + 30)
                
                # Calculate arc points
                points = []
                for deg in range(int(math.degrees(start_angle)), int(math.degrees(end_angle)) + 1, 10):
                    rad = math.radians(deg)
                    x = self.position[0] + math.cos(rad) * (size - 4)
                    y = self.position[1] + math.sin(rad) * (size - 4)
                    points.append((x, y))
                
                if len(points) > 1:
                    pygame.draw.lines(screen, self.color, False, points, 2)
        
        elif self.type == 'spread_shot':
            # Draw spread shot symbol (three lines)
            angles = [-30, 0, 30]
            for angle in angles:
                rad_angle = math.radians(angle + self.angle)
                end_x = self.position[0] + math.cos(rad_angle) * (size - 4)
                end_y = self.position[1] + math.sin(rad_angle) * (size - 4)
                pygame.draw.line(
                    screen,
                    self.color,
                    self.position,
                    (end_x, end_y),
                    2
                )
        elif self.type == PowerupType.RAPID_FIRE:
            # Draw rapid fire symbol (lightning bolt)
            points = [
                self.position + Vector2(-size/2, -size/2),
                self.position + Vector2(0, 0),
                self.position + Vector2(-size/2, size/2)
            ]
            pygame.draw.lines(screen, self.color, False, points, 2)
        elif self.type == PowerupType.INVINCIBILITY:
            # Draw invincibility symbol (star)
            points = []
            for i in range(5):
                angle = (i * 144 - 90) * math.pi / 180
                points.append(self.position + Vector2(
                    math.cos(angle) * size,
                    math.sin(angle) * size
                ))
            pygame.draw.polygon(screen, self.color, points, 2) 