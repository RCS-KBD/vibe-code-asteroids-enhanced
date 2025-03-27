"""Enemy module for alien ships."""

import random
import pygame
import math
from typing import List, Tuple

class Enemy:
    """Represents an alien ship that moves in patterns and shoots at the player."""
    
    def __init__(self, screen_width: int, screen_height: int):
        """Initialize the enemy ship.
        
        Args:
            screen_width: Width of the game screen
            screen_height: Height of the game screen
        """
        self.screen_width = screen_width
        self.screen_height = screen_height
        
        # Randomly choose starting position on one of the screen edges
        if random.random() < 0.5:
            # Start on left or right edge
            self.x = 0 if random.random() < 0.5 else screen_width
            self.y = random.randint(0, screen_height)
        else:
            # Start on top or bottom edge
            self.x = random.randint(0, screen_width)
            self.y = 0 if random.random() < 0.5 else screen_height
        
        # Movement properties
        self.speed = 3
        self.angle = random.uniform(0, 2 * math.pi)
        self.rotation_speed = 0.02
        self.direction_timer = random.randint(60, 180)  # Frames until next direction change
        
        # Combat properties
        self.size = 20
        self.health = 2
        self.shoot_timer = random.randint(30, 90)  # Frames until next shot
        self.is_dead = False
        
        # Create the enemy ship's shape (triangle pointing in direction of travel)
        self.vertices = self._create_vertices()
        
        # Collision circle
        self.radius = self.size
    
    def _create_vertices(self) -> List[Tuple[float, float]]:
        """Create the vertices for the enemy ship shape.
        
        Returns:
            List of (x, y) tuples defining the ship's shape
        """
        # Create a triangular shape
        vertices = [
            (self.size, 0),           # Nose
            (-self.size, self.size),  # Back right
            (-self.size, -self.size)  # Back left
        ]
        return vertices
    
    def update(self, player_pos: Tuple[float, float]) -> None:
        """Update the enemy's position and state.
        
        Args:
            player_pos: (x, y) tuple of player's current position
        """
        # Update direction timer and change direction if needed
        self.direction_timer -= 1
        if self.direction_timer <= 0:
            # Choose new random direction
            self.angle = random.uniform(0, 2 * math.pi)
            self.direction_timer = random.randint(60, 180)
        
        # Move in current direction
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        
        # Wrap around screen edges
        self.x = self.x % self.screen_width
        self.y = self.y % self.screen_height
        
        # Update shoot timer
        self.shoot_timer -= 1
    
    def should_shoot(self) -> bool:
        """Check if the enemy should shoot.
        
        Returns:
            True if it's time to shoot, False otherwise
        """
        if self.shoot_timer <= 0:
            self.shoot_timer = random.randint(30, 90)
            return True
        return False
    
    def get_bullet_direction(self, player_pos: Tuple[float, float]) -> float:
        """Calculate direction to shoot towards player.
        
        Args:
            player_pos: (x, y) tuple of player's current position
            
        Returns:
            Angle in radians for bullet direction
        """
        dx = player_pos[0] - self.x
        dy = player_pos[1] - self.y
        return math.atan2(dy, dx)
    
    def take_damage(self) -> None:
        """Handle the enemy taking damage."""
        self.health -= 1
        if self.health <= 0:
            self.is_dead = True
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the enemy ship on the screen.
        
        Args:
            screen: Pygame surface to draw on
        """
        # Transform vertices based on position and rotation
        transformed_vertices = []
        for x, y in self.vertices:
            # Rotate point
            rotated_x = x * math.cos(self.angle) - y * math.sin(self.angle)
            rotated_y = x * math.sin(self.angle) + y * math.cos(self.angle)
            # Translate to position
            transformed_vertices.append((
                int(rotated_x + self.x),
                int(rotated_y + self.y)
            ))
        
        # Draw the ship
        pygame.draw.polygon(screen, (255, 0, 0), transformed_vertices, 2)
        
        # Draw health indicator (small dots below ship)
        for i in range(self.health):
            pygame.draw.circle(screen, (255, 0, 0),
                (int(self.x - (self.health - 1) * 5 + i * 10),
                 int(self.y + self.size + 10)), 2)