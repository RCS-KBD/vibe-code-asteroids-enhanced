"""Player entity module."""

import pygame
from pygame import Vector2
import math
from typing import List, Tuple
from ..utils.constants import (
    WIDTH, HEIGHT, WHITE, BLUE, YELLOW,
    SHIP_SIZE, PLAYER_ACCELERATION, PLAYER_FRICTION,
    PLAYER_MAX_SPEED, PLAYER_SHIELD_RADIUS,
    PLAYER_INVULNERABLE_TIME, POWERUP_DURATION,
    INVULNERABILITY_DURATION, PLAYER_ROTATION_SPEED
)

class Player:
    """Player controlled ship."""
    
    def __init__(self, x: float, y: float) -> None:
        """Initialize the player ship."""
        # Position and movement
        self.position = [float(x), float(y)]
        self.velocity = [0.0, 0.0]
        self.acceleration = PLAYER_ACCELERATION
        self.friction = PLAYER_FRICTION
        self.rotation = 0.0  # Degrees, 0 is pointing up
        self.size = SHIP_SIZE
        
        # Status effects
        self.is_invulnerable = False
        self.invulnerable_timer = 0
        self.shields = 0
        
        # Spread shot properties
        self.spread_shot = False
        self.spread_shot_timer = 0
        
        # Create collision rect
        self.rect = pygame.Rect(
            x - self.size // 2,
            y - self.size // 2,
            self.size,
            self.size
        )
        
        # Visual effects
        self.shield_pulse = 0
        self.shield_pulse_direction = 1

    def thrust(self) -> None:
        """Apply thrust in the direction the ship is facing."""
        # Convert rotation to radians (subtract 90 to make 0 degrees point right)
        angle = math.radians(self.rotation - 90)
        
        # Calculate thrust vector
        thrust_x = math.cos(angle) * self.acceleration
        thrust_y = math.sin(angle) * self.acceleration
        
        # Apply thrust to velocity
        self.velocity[0] += thrust_x
        self.velocity[1] += thrust_y
        
        # Limit speed
        speed = math.sqrt(self.velocity[0]**2 + self.velocity[1]**2)
        if speed > PLAYER_MAX_SPEED:
            scale = PLAYER_MAX_SPEED / speed
            self.velocity[0] *= scale
            self.velocity[1] *= scale

    def get_nose_position(self) -> List[float]:
        """Calculate the position of the ship's nose for bullet spawning."""
        # Convert rotation to radians (subtract 90 to make 0 degrees point right)
        angle = math.radians(self.rotation - 90)
        # Calculate nose position one ship size in front of the ship
        nose_x = self.position[0] + math.cos(angle) * self.size
        nose_y = self.position[1] + math.sin(angle) * self.size
        return [nose_x, nose_y]

    def update(self) -> None:
        """Update player state including position, powerups, and timers."""
        # Handle keyboard input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.rotation = (self.rotation - PLAYER_ROTATION_SPEED) % 360
        if keys[pygame.K_RIGHT]:
            self.rotation = (self.rotation + PLAYER_ROTATION_SPEED) % 360
        if keys[pygame.K_UP]:
            self.thrust()
        if keys[pygame.K_SPACE]:
            # Shooting is handled by the game manager
            pass
        
        # Apply friction
        self.velocity[0] *= self.friction
        self.velocity[1] *= self.friction
        
        # Update position
        self.position[0] += self.velocity[0]
        self.position[1] += self.velocity[1]
        
        # Wrap around screen edges
        self.position[0] = self.position[0] % WIDTH
        self.position[1] = self.position[1] % HEIGHT
        
        # Update collision rect
        self.rect.center = self.position
        
        # Update spread shot timer
        if self.spread_shot:
            self.spread_shot_timer -= 1
            if self.spread_shot_timer <= 0:
                self.spread_shot = False

        # Update invulnerability timer
        if self.is_invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False
        
        # Update shield pulse effect
        if self.shields > 0:
            self.shield_pulse += 0.1 * self.shield_pulse_direction
            if self.shield_pulse >= 1:
                self.shield_pulse = 1
                self.shield_pulse_direction = -1
            elif self.shield_pulse <= 0:
                self.shield_pulse = 0
                self.shield_pulse_direction = 1

    def draw(self, screen: pygame.Surface) -> None:
        """Draw the player ship.
        
        Args:
            screen: Surface to draw on
        """
        # Don't draw if invulnerable and should be blinking
        if self.is_invulnerable and pygame.time.get_ticks() % 200 < 100:
            return
        
        # Calculate ship vertices
        angle = math.radians(self.rotation - 90)  # -90 to make 0 degrees point right
        cos_a = math.cos(angle)
        sin_a = math.sin(angle)
        
        # Ship points relative to center (pointing right by default)
        points = [
            (self.size, 0),  # Nose (right)
            (-self.size // 2, -self.size // 2),  # Top wing
            (-self.size // 4, 0),  # Back center
            (-self.size // 2, self.size // 2)  # Bottom wing
        ]
        
        # Transform points
        transformed_points = []
        for x, y in points:
            # Rotate
            rx = x * cos_a - y * sin_a
            ry = x * sin_a + y * cos_a
            # Translate
            px = self.position[0] + rx
            py = self.position[1] + ry
            transformed_points.append((px, py))
        
        # Draw ship outline
        pygame.draw.lines(screen, WHITE, True, transformed_points, 2)
        
        # Draw shield if active
        if self.shields > 0:
            # Shield color (light blue)
            SHIELD_COLOR = (64, 128, 255)
            
            # Draw shield circle
            pygame.draw.circle(
                screen,
                SHIELD_COLOR,
                (int(self.position[0]), int(self.position[1])),
                self.size + 10,
                1
            )
            # Draw additional shield effects
            shield_time = pygame.time.get_ticks()
            shield_pulse = abs(math.sin(shield_time * 0.01)) * 5
            pygame.draw.circle(
                screen,
                SHIELD_COLOR,
                (int(self.position[0]), int(self.position[1])),
                self.size + 10 + shield_pulse,
                1
            )
        
        # Draw debug invincibility effect
        if hasattr(self, 'debug_invincible') and self.debug_invincible:
            # Draw white invincibility circle with pulsing effect
            current_time = pygame.time.get_ticks()
            pulse = abs(math.sin(current_time * 0.01)) * 8
            
            # Inner circle
            pygame.draw.circle(
                screen,
                WHITE,
                (int(self.position[0]), int(self.position[1])),
                self.size + 15,
                2
            )
            # Outer pulsing circle
            pygame.draw.circle(
                screen,
                WHITE,
                (int(self.position[0]), int(self.position[1])),
                self.size + 15 + pulse,
                1
            )
        
        # Draw spread shot indicator if active
        if self.spread_shot:
            self._draw_spread_shot_indicators(screen)

    def _draw_shield_bubble(self, screen):
        """Draw the shield bubble effect."""
        radius = PLAYER_SHIELD_RADIUS + int(self.shield_pulse * 4)
        pygame.draw.circle(
            screen,
            (100, 100, 255),
            [int(self.position[0]), int(self.position[1])],
            radius,
            1
        )

    def _draw_shield_indicators(self, screen):
        """Draw shield count indicators."""
        for i in range(self.shields):
            x = self.position[0] + math.cos(math.radians(i * 360 / 3)) * 20
            y = self.position[1] + math.sin(math.radians(i * 360 / 3)) * 20
            pygame.draw.circle(screen, (100, 100, 255), (int(x), int(y)), 2)

    def _draw_spread_shot_indicators(self, screen):
        """Draw spread shot indicator."""
        angles = [-15, 0, 15]
        for angle in angles:
            rad_angle = math.radians(self.rotation - 90 + angle)
            end_x = self.position[0] + math.cos(rad_angle) * (self.size + 10)
            end_y = self.position[1] + math.sin(rad_angle) * (self.size + 10)
            pygame.draw.line(
                screen,
                (0, 255, 0),
                self.position,
                (end_x, end_y),
                1
            )

    def activate_spread_shot(self) -> None:
        """Activate the spread shot powerup."""
        self.spread_shot = True
        self.spread_shot_timer = POWERUP_DURATION

    def add_shield(self) -> None:
        """Add a shield to the player."""
        self.shields += 1

    def remove_shield(self) -> None:
        """Remove a shield from the player."""
        if self.shields > 0:
            self.shields -= 1

    def make_invulnerable(self):
        """Make the player temporarily invulnerable."""
        self.is_invulnerable = True
        self.invulnerable_timer = PLAYER_INVULNERABLE_TIME

    def update_spread_shot_timer(self):
        """Update the spread shot timer."""
        if self.spread_shot:
            self.spread_shot_timer -= 1
            if self.spread_shot_timer <= 0:
                self.spread_shot = False

    def update_shield_pulse(self):
        """Update the shield pulse effect."""
        if self.shields > 0:
            self.shield_pulse += 0.1 * self.shield_pulse_direction
            if self.shield_pulse >= 1:
                self.shield_pulse = 1
                self.shield_pulse_direction = -1
            elif self.shield_pulse <= 0:
                self.shield_pulse = 0
                self.shield_pulse_direction = 1

    def update_invulnerability(self):
        """Update the invulnerability timer."""
        if self.is_invulnerable:
            self.invulnerable_timer -= 1
            if self.invulnerable_timer <= 0:
                self.is_invulnerable = False
        
    def update_shield_count(self):
        """Update the shield count."""
        if self.shields < 3:
            self.shields += 1

    def update_spread_shot_indicators(self, screen):
        """Update the spread shot indicators."""
        angles = [-15, 0, 15]
        for angle in angles:
            rad_angle = math.radians(self.rotation - 90 + angle)
            end_x = self.position[0] + math.cos(rad_angle) * (self.size + 10)
            end_y = self.position[1] + math.sin(rad_angle) * (self.size + 10)
            pygame.draw.line(
                screen,
                (0, 255, 0),
                self.position,
                (end_x, end_y),
                1
            ) 