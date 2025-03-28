"""Asteroid module."""

import math
import random
import pygame
from src.utils.constants import (
    WIDTH, HEIGHT, WHITE,
    ASTEROID_SIZES, ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX,
    ASTEROID_VERTICES_MIN, ASTEROID_VERTICES_MAX
)

class Asteroid:
    """Asteroid class representing space rocks."""

    def __init__(self, x: float, y: float, size: str = 'large'):
        """Initialize the asteroid.
        
        Args:
            x: Initial x position
            y: Initial y position
            size: Size of asteroid ('large', 'medium', or 'small')
        """
        self.position = [float(x), float(y)]
        self.size_name = size
        
        # Set size based on asteroid type
        if size == 'large':
            self.radius = 40
        elif size == 'medium':
            self.radius = 20
        else:  # small
            self.radius = 10
            
        # Random velocity
        angle = random.random() * math.pi * 2
        speed = random.uniform(1, 3)
        self.velocity = [
            math.cos(angle) * speed,
            math.sin(angle) * speed
        ]
        
        # Random rotation
        self.rotation = 0
        self.rotation_speed = random.uniform(-2, 2)
        
        # Generate vertices for the asteroid shape
        self._generate_vertices()
        
        # Create collision rectangle
        self.rect = pygame.Rect(
            x - self.radius,
            y - self.radius,
            self.radius * 2,
            self.radius * 2
        )

    def _generate_vertices(self):
        """Generate random vertices for the asteroid shape."""
        num_vertices = random.randint(
            ASTEROID_VERTICES_MIN,
            ASTEROID_VERTICES_MAX
        )
        vertices = []
        
        for i in range(num_vertices):
            angle = (i / num_vertices) * math.pi * 2
            # Random radius between 80% and 120% of base radius
            radius = self.radius * random.uniform(0.8, 1.2)
            x = math.cos(angle) * radius
            y = math.sin(angle) * radius
            vertices.append((x, y))
            
        self.vertices = vertices

    def update(self):
        """Update asteroid position and rotation."""
        # Update position
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        
        # Wrap around screen edges
        self.position[0] = self.position[0] % WIDTH
        self.position[1] = self.position[1] % HEIGHT
        
        # Update rotation
        self.rotation += self.rotation_speed
        
        # Update collision rectangle
        self.rect.center = self.position

    def draw(self, screen):
        """Draw the asteroid."""
        # Transform vertices
        transformed_points = []
        angle = math.radians(self.rotation)
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        for x, y in self.vertices:
            # Rotate
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            # Translate
            px = self.position[0] + rx
            py = self.position[1] + ry
            transformed_points.append((px, py))
        
        # Draw asteroid outline
        pygame.draw.lines(screen, WHITE, True, transformed_points, 2)
        
        # Draw additional lines for visual interest
        for i in range(len(transformed_points)):
            if i % 2 == 0:
                start = transformed_points[i]
                end = transformed_points[(i + len(transformed_points)//2) % len(transformed_points)]
                pygame.draw.line(screen, WHITE, start, end, 1)

    def split(self) -> list['Asteroid']:
        """Split the asteroid into smaller pieces.
        
        Returns:
            list[Asteroid]: List of new asteroids (empty if already small)
        """
        if self.size_name == 'small':
            return []
        
        new_size = 'medium' if self.size_name == 'large' else 'small'
        
        return [
            Asteroid(self.position[0], self.position[1], new_size),
            Asteroid(self.position[0], self.position[1], new_size)
        ]
    
    def get_points(self) -> int:
        """Get the point value for destroying this asteroid.
        
        Returns:
            int: Points awarded for destruction
        """
        points = {
            'large': 20,
            'medium': 50,
            'small': 100
        }
        return points[self.size_name]

    @property
    def size(self) -> float:
        """Get the collision radius of the asteroid."""
        return self.radius 