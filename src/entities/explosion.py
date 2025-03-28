"""Explosion module."""

import random
import math
import pygame
from src.utils.constants import (
    EXPLOSION_DURATION,
    EXPLOSION_PARTICLE_COUNT,
    EXPLOSION_PARTICLE_SPEED,
    EXPLOSION_PARTICLE_SIZE,
    EXPLOSION_COLORS
)

class Explosion:
    """Explosion class representing particle effects."""

    def __init__(self, x: float, y: float):
        """Initialize the explosion.
        
        Args:
            x: X position of explosion center
            y: Y position of explosion center
        """
        self.position = [float(x), float(y)]
        self.particles = []
        self.lifetime = EXPLOSION_DURATION
        self.is_finished = False
        
        # Create particles
        for _ in range(EXPLOSION_PARTICLE_COUNT):
            # Random angle and speed
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, EXPLOSION_PARTICLE_SPEED)
            
            # Calculate velocity
            velocity = [
                math.cos(angle) * speed,
                math.sin(angle) * speed
            ]
            
            # Random color from explosion colors
            color = random.choice(EXPLOSION_COLORS)
            
            # Random size variation
            size = random.randint(
                EXPLOSION_PARTICLE_SIZE - 1,
                EXPLOSION_PARTICLE_SIZE + 1
            )
            
            # Add particle
            self.particles.append({
                'position': [x, y],
                'velocity': velocity,
                'color': color,
                'size': size,
                'alpha': 255
            })

    def update(self):
        """Update explosion particles."""
        # Update lifetime
        self.lifetime -= 1
        if self.lifetime <= 0:
            self.is_finished = True
            return
        
        # Calculate fade based on lifetime
        fade_factor = self.lifetime / EXPLOSION_DURATION
        
        # Update particles
        for particle in self.particles:
            # Update position
            particle['position'][0] += particle['velocity'][0]
            particle['position'][1] += particle['velocity'][1]
            
            # Update velocity (add some randomness)
            particle['velocity'][0] *= 0.95
            particle['velocity'][1] *= 0.95
            particle['velocity'][0] += random.uniform(-0.1, 0.1)
            particle['velocity'][1] += random.uniform(-0.1, 0.1)
            
            # Update alpha
            particle['alpha'] = int(255 * fade_factor)

    def draw(self, screen):
        """Draw explosion particles."""
        for particle in self.particles:
            # Skip if fully transparent
            if particle['alpha'] <= 0:
                continue
            
            # Create surface for particle
            surf = pygame.Surface((particle['size'] * 2, particle['size'] * 2))
            surf.set_colorkey((0, 0, 0))
            
            # Draw particle
            pygame.draw.circle(
                surf,
                particle['color'],
                (particle['size'], particle['size']),
                particle['size']
            )
            
            # Set alpha
            surf.set_alpha(particle['alpha'])
            
            # Draw to screen
            screen.blit(
                surf,
                (
                    particle['position'][0] - particle['size'],
                    particle['position'][1] - particle['size']
                )
            ) 