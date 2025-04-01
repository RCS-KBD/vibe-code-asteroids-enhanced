"""Game manager module."""

import pygame
from pygame import Vector2
import random
import logging
from typing import List, Optional
from src.entities.player import Player
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.entities.powerup import Powerup, PowerupType
from src.entities.explosion import Explosion
from src.entities.enemy import Enemy  # Import the Enemy class
from src.managers.sound_manager import SoundManager
from src.utils.constants import (
    WIDTH, HEIGHT, POWERUP_SPAWN_CHANCE,
    STARTING_LIVES, STARTING_ASTEROIDS,
    ASTEROID_SPAWN_DISTANCE, WHITE,
    ENEMY_SPAWN_TIME_MIN, ENEMY_SPAWN_TIME_MAX
)

class GameManager:
    """Manages game state, entities, and level progression."""
    
    def __init__(self, screen: pygame.Surface, sound_manager: SoundManager):
        """Initialize the game manager.
        
        Args:
            screen: Pygame surface to draw on
            sound_manager: Sound manager instance
        """
        self.logger = logging.getLogger(__name__)
        self.screen = screen
        self.sound_manager = sound_manager
        
        # Initialize game state
        self.score = 0
        self.level = 1
        self.lives = 1  # Changed to single life system
        self.game_over = False
        self.level_complete = False
        self.level_complete_timer = 0
        self.paused = False
        self.respawn_timer = 0
        self.show_debug = False
        self.debug_invincible = False
        
        # Initialize game objects
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        self.player.debug_invincible = False  # Initialize player's debug invincibility state
        self.asteroids = []
        self.bullets = []
        self.powerups = []
        self.enemies = []
        self.explosions = []
        
        # Initialize timers
        self.enemy_spawn_timer = random.randint(
            ENEMY_SPAWN_TIME_MIN,
            ENEMY_SPAWN_TIME_MAX
        )
        
        # Spawn initial asteroids
        self._spawn_level_asteroids()
        self.logger.info("Game manager initialized")
    
    def _spawn_level_asteroids(self) -> None:
        """Spawn asteroids for the current level."""
        num_asteroids = STARTING_ASTEROIDS + (self.level - 1) * 2
        
        for _ in range(num_asteroids):
            # Generate position away from player
            while True:
                x = random.randint(0, WIDTH)
                y = random.randint(0, HEIGHT)
                dx = x - self.player.position[0]
                dy = y - self.player.position[1]
                distance = (dx * dx + dy * dy) ** 0.5
                if distance > ASTEROID_SPAWN_DISTANCE:
                    break
            
            self.asteroids.append(Asteroid(x, y, 'large'))
        
        self.logger.debug(f"Spawned {num_asteroids} asteroids for level {self.level}")
    
    def _spawn_powerup(self, position: Vector2) -> None:
        """Possibly spawn a powerup at the given position.
        
        Args:
            position: Position to spawn the powerup
        """
        if random.random() < POWERUP_SPAWN_CHANCE:
            self.powerups.append(Powerup(position))
            self.logger.debug(f"Spawned powerup at {position}")
    
    def _find_safe_spawn_position(self) -> List[float]:
        """Find a safe position away from asteroids to respawn the player."""
        best_pos = [WIDTH // 2, HEIGHT // 2]
        best_distance = 0
        
        # Try several random positions
        for _ in range(20):
            x = random.randint(100, WIDTH - 100)
            y = random.randint(100, HEIGHT - 100)
            min_distance = float('inf')
            
            # Find minimum distance to any asteroid
            for asteroid in self.asteroids:
                dx = x - asteroid.position[0]
                dy = y - asteroid.position[1]
                distance = (dx * dx + dy * dy) ** 0.5
                min_distance = min(min_distance, distance)
            
            # Update best position if this one is safer
            if min_distance > best_distance:
                best_distance = min_distance
                best_pos = [x, y]
        
        return best_pos
    
    def update(self) -> None:
        """Update game state."""
        if self.game_over:
            # Check for retry input
            keys = pygame.key.get_pressed()
            if keys[pygame.K_r]:
                self.reset_game()
            return
            
        if self.paused or self.respawn_timer > 0:
            self.respawn_timer = max(0, self.respawn_timer - 1)
            return
        
        # Sync debug invincibility with player
        self.player.debug_invincible = self.debug_invincible
        
        # Update player
        self.player.update()
        
        # Update enemy spawn timer - only in level 2 and above, and only if no enemies present
        if self.level >= 2 and len(self.enemies) == 0:
            self.enemy_spawn_timer -= 1
            if self.enemy_spawn_timer <= 0:
                self.enemies.append(Enemy(WIDTH, HEIGHT))
                # Longer delay between enemy spawns
                self.enemy_spawn_timer = random.randint(
                    ENEMY_SPAWN_TIME_MIN * 2,  # Double the minimum time
                    ENEMY_SPAWN_TIME_MAX * 2   # Double the maximum time
                )
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet.update()
            if bullet.lifetime <= 0:
                self.bullets.remove(bullet)
        
        # Update asteroids
        for asteroid in self.asteroids[:]:
            asteroid.update()
        
        # Update powerups
        for powerup in self.powerups[:]:
            powerup.update()
            if powerup.lifetime <= 0:
                self.powerups.remove(powerup)
        
        # Update enemies and handle their shooting
        for enemy in self.enemies[:]:
            enemy.update((self.player.position[0], self.player.position[1]))
            if enemy.should_shoot():
                # Create enemy bullet
                direction = enemy.get_bullet_direction((self.player.position[0], self.player.position[1]))
                bullet = Bullet(
                    [enemy.x, enemy.y],  # Use enemy position
                    direction,
                    is_enemy=True
                )
                self.bullets.append(bullet)
                self.sound_manager.play('shoot')
        
        # Update explosions
        for explosion in self.explosions[:]:
            explosion.update()
            if explosion.is_finished:
                self.explosions.remove(explosion)
        
        # Check collisions
        self._check_collisions()
        
        # Check level completion - require both asteroids and enemies to be cleared
        if not self.asteroids and not self.enemies and not self.level_complete:
            self.level_complete = True
            self.sound_manager.play('level_complete')
    
    def reset_game(self) -> None:
        """Reset the game state for a new game."""
        self.score = 0
        self.level = 1
        self.lives = 1
        self.game_over = False
        self.level_complete = False
        self.paused = False
        self.respawn_timer = 0
        
        # Reset player
        self.player = Player(WIDTH // 2, HEIGHT // 2)
        
        # Clear entity lists
        self.asteroids.clear()
        self.bullets.clear()
        self.powerups.clear()
        self.enemies.clear()
        self.explosions.clear()
        
        # Reset enemy spawn timer to a high value for level 1 (won't be used)
        self.enemy_spawn_timer = ENEMY_SPAWN_TIME_MAX * 2
        
        # Spawn initial asteroids
        self._spawn_level_asteroids()
        
        self.logger.info("Game reset")
    
    def _check_collisions(self) -> None:
        """Check for collisions between game objects."""
        # Asteroid-asteroid collisions
        for i, asteroid1 in enumerate(self.asteroids[:-1]):
            for asteroid2 in self.asteroids[i + 1:]:
                if asteroid1.rect.colliderect(asteroid2.rect):
                    # Calculate collision normal
                    dx = asteroid2.position[0] - asteroid1.position[0]
                    dy = asteroid2.position[1] - asteroid1.position[1]
                    dist = (dx * dx + dy * dy) ** 0.5
                    if dist == 0:  # Avoid division by zero
                        continue
                        
                    # Normalize the collision vector
                    nx = dx / dist
                    ny = dy / dist
                    
                    # Relative velocity
                    rvx = asteroid2.velocity[0] - asteroid1.velocity[0]
                    rvy = asteroid2.velocity[1] - asteroid1.velocity[1]
                    
                    # Relative velocity along normal
                    rv_normal = rvx * nx + rvy * ny
                    
                    # Don't collide if asteroids are moving apart
                    if rv_normal > 0:
                        continue
                    
                    # Coefficient of restitution (bounciness)
                    restitution = 0.8
                    
                    # Calculate impulse scalar
                    j = -(1 + restitution) * rv_normal
                    j *= 0.5  # Equal mass assumption
                    
                    # Apply impulse
                    asteroid1.velocity[0] -= j * nx
                    asteroid1.velocity[1] -= j * ny
                    asteroid2.velocity[0] += j * nx
                    asteroid2.velocity[1] += j * ny
                    
                    # Separate the asteroids to prevent sticking
                    overlap = (asteroid1.size + asteroid2.size) - dist
                    if overlap > 0:
                        asteroid1.position[0] -= overlap * nx * 0.5
                        asteroid1.position[1] -= overlap * ny * 0.5
                        asteroid2.position[0] += overlap * nx * 0.5
                        asteroid2.position[1] += overlap * ny * 0.5
        
        # Bullet-asteroid collisions
        for bullet in self.bullets[:]:
            # Skip enemy bullets for asteroid collisions
            if bullet.is_enemy:
                continue
                
            for asteroid in self.asteroids[:]:
                if bullet.rect.colliderect(asteroid.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)
                    
                    # Create explosion
                    self.explosions.append(
                        Explosion(asteroid.position[0], asteroid.position[1])
                    )
                    self.sound_manager.play('explosion')
                    
                    # Split asteroid if large or medium
                    if asteroid.size_name != 'small':
                        new_size = 'medium' if asteroid.size_name == 'large' else 'small'
                        for _ in range(2):
                            self.asteroids.append(
                                Asteroid(
                                    asteroid.position[0],
                                    asteroid.position[1],
                                    new_size
                                )
                            )
                    
                    # Add score
                    score_values = {
                        'large': 20,
                        'medium': 50,
                        'small': 100
                    }
                    self.score += score_values[asteroid.size_name]
                    
                    # Spawn powerup
                    if random.random() < POWERUP_SPAWN_CHANCE:
                        self.powerups.append(
                            Powerup(
                                asteroid.position[0],
                                asteroid.position[1],
                                random.choice(['shield', 'spread_shot'])
                            )
                        )
                    break
        
        # Player-asteroid collisions
        for asteroid in self.asteroids[:]:
            if self.player.rect.colliderect(asteroid.rect):
                if self.debug_invincible:
                    # Destroy asteroid with invincibility
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)
                        # Create explosion
                        self.explosions.append(
                            Explosion(asteroid.position[0], asteroid.position[1])
                        )
                        self.sound_manager.play('explosion')
                        
                        # Add score
                        score_values = {
                            'large': 20,
                            'medium': 50,
                            'small': 100
                        }
                        self.score += score_values[asteroid.size_name]
                        
                        # Chance to spawn powerup
                        if random.random() < POWERUP_SPAWN_CHANCE:
                            self.powerups.append(
                                Powerup(
                                    asteroid.position[0],
                                    asteroid.position[1],
                                    random.choice(['shield', 'spread_shot'])
                                )
                            )
                elif not self.player.is_invulnerable:
                    if self.player.shields > 0:
                        # Remove shield and create shield break effect
                        self.player.remove_shield()
                        self.sound_manager.play('shield_hit')
                        # Create shield break explosion
                        self.explosions.append(
                            Explosion(
                                self.player.position[0],
                                self.player.position[1]
                            )
                        )
                        # Make player briefly invulnerable
                        self.player.make_invulnerable()
                    else:
                        # Game over on hit (single life system)
                        self.game_over = True
                        self.sound_manager.play('explosion')
                        
                        # Create explosion at player position
                        self.explosions.append(
                            Explosion(
                                self.player.position[0],
                                self.player.position[1]
                            )
                        )
        
        # Player-powerup collisions
        for powerup in self.powerups[:]:
            if self.player.rect.colliderect(powerup.rect):
                if powerup.type == 'shield':
                    self.player.add_shield()
                elif powerup.type == 'spread_shot':
                    self.player.activate_spread_shot()
                self.powerups.remove(powerup)
                self.sound_manager.play('powerup')
                break
        
        # Enemy-bullet collisions (player bullets hitting enemies)
        for enemy in self.enemies[:]:
            # First check for player-enemy collisions
            if self.player.rect.colliderect(enemy.rect):
                if self.debug_invincible:
                    # Destroy enemy with invincibility
                    if enemy in self.enemies:
                        self.enemies.remove(enemy)
                        # Create explosion
                        self.explosions.append(
                            Explosion(enemy.x, enemy.y)
                        )
                        self.score += 500
                        self.sound_manager.play('explosion')
                        
                        # Chance to spawn powerup from destroyed enemy
                        if random.random() < POWERUP_SPAWN_CHANCE:
                            self.powerups.append(
                                Powerup(
                                    enemy.x,
                                    enemy.y,
                                    random.choice(['shield', 'spread_shot'])
                                )
                            )
                elif not self.player.is_invulnerable:
                    if self.player.shields > 0:
                        # Remove shield and create shield break effect
                        self.player.remove_shield()
                        self.sound_manager.play('shield_hit')
                        # Create shield break explosion
                        self.explosions.append(
                            Explosion(
                                self.player.position[0],
                                self.player.position[1]
                            )
                        )
                        # Make player briefly invulnerable
                        self.player.make_invulnerable()
                    else:
                        # Game over on hit (single life system)
                        self.game_over = True
                        self.sound_manager.play('explosion')
                        # Create explosion at player position
                        self.explosions.append(
                            Explosion(
                                self.player.position[0],
                                self.player.position[1]
                            )
                        )
                continue  # Skip bullet collision checks for this enemy if it was destroyed by player collision

            # Then check bullet collisions
            for bullet in self.bullets[:]:
                # Skip enemy bullets for enemy collisions
                if bullet.is_enemy:
                    continue
                    
                if bullet.rect.colliderect(enemy.rect):
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    enemy.take_damage()
                    if enemy.is_dead:
                        if enemy in self.enemies:
                            self.enemies.remove(enemy)
                            self.explosions.append(
                                Explosion(enemy.x, enemy.y)
                            )
                            self.score += 500
                            self.sound_manager.play('explosion')
                            
                            # Chance to spawn powerup from destroyed enemy
                            if random.random() < POWERUP_SPAWN_CHANCE:
                                self.powerups.append(
                                    Powerup(
                                        enemy.x,
                                        enemy.y,
                                        random.choice(['shield', 'spread_shot'])
                                    )
                                )
                    break

        # Player-bullet collisions (enemy bullets hitting player)
        for bullet in self.bullets[:]:
            if bullet.is_enemy and bullet.rect.colliderect(self.player.rect):
                # Create explosion effect regardless of invincibility
                self.explosions.append(
                    Explosion(bullet.position[0], bullet.position[1])
                )
                self.sound_manager.play('explosion')
                
                if not self.player.is_invulnerable and not self.debug_invincible:
                    if self.player.shields > 0:
                        # Remove shield and create shield break effect
                        self.player.remove_shield()
                        self.sound_manager.play('shield_hit')
                        # Create shield break explosion
                        self.explosions.append(
                            Explosion(
                                self.player.position[0],
                                self.player.position[1]
                            )
                        )
                        # Make player briefly invulnerable
                        self.player.make_invulnerable()
                    else:
                        # Game over on hit (single life system)
                        self.game_over = True
                        self.sound_manager.play('explosion')
                        # Create explosion at player position
                        self.explosions.append(
                            Explosion(
                                self.player.position[0],
                                self.player.position[1]
                            )
                        )
                
                # Remove the bullet regardless of player state
                if bullet in self.bullets:
                    self.bullets.remove(bullet)
                break
    
    def start_next_level(self) -> None:
        """Start the next level."""
        self.level += 1
        self.level_complete = False
        self.level_complete_timer = 0
        
        # Reset player position and state
        self.player.position = Vector2(WIDTH // 2, HEIGHT // 2)
        self.player.velocity = Vector2(0, 0)
        self.player.make_invulnerable()  # Give brief invulnerability on level start
        
        # Clear all entities except player
        self.bullets.clear()
        self.powerups.clear()
        self.enemies.clear()
        self.explosions.clear()
        
        # Reset enemy spawn timer
        self.enemy_spawn_timer = random.randint(
            ENEMY_SPAWN_TIME_MIN,
            ENEMY_SPAWN_TIME_MAX
        )
        
        # Spawn new asteroids
        self._spawn_level_asteroids()
        
        self.logger.info(f"Starting level {self.level}")
    
    def shoot(self) -> None:
        """Create bullets from the player's position."""
        if not self.game_over and not self.paused:
            if self.player.spread_shot:
                angles = [-15, 0, 15]  # Spread angles in degrees
                for angle in angles:
                    self.bullets.append(
                        Bullet(
                            self.player.get_nose_position(),
                            self.player.rotation + angle
                        )
                    )
            else:
                self.bullets.append(
                    Bullet(
                        self.player.get_nose_position(),
                        self.player.rotation
                    )
                )
            self.sound_manager.play('shoot')
    
    def draw(self) -> None:
        """Draw all game objects.
        
        Args:
            screen: Surface to draw on
        """
        # Draw all entities
        self.player.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
            
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
            
        for powerup in self.powerups:
            powerup.draw(self.screen)
            
        for enemy in self.enemies:
            enemy.draw(self.screen)
        
        for explosion in self.explosions:
            explosion.draw(self.screen)
        
        # Draw HUD
        self._draw_hud()
        if self.show_debug:
            self._draw_debug_menu()
    
    def _draw_hud(self):
        """Draw the heads-up display."""
        try:
            # Use system font as fallback if default font fails
            try:
                font = pygame.font.Font(None, 36)
            except:
                font = pygame.font.SysFont('arial', 36)
            
            # Draw score and level
            score_text = font.render(f"Score: {self.score}", True, WHITE)
            self.screen.blit(score_text, (10, 10))
            
            level_text = font.render(f"Level: {self.level}", True, WHITE)
            level_rect = level_text.get_rect()
            level_rect.topright = (WIDTH - 10, 10)
            self.screen.blit(level_text, level_rect)
            
            # Draw remaining enemies count in level 2+
            if self.level >= 2:
                enemy_text = font.render(f"Enemies: {len(self.enemies)}", True, WHITE)
                enemy_rect = enemy_text.get_rect()
                enemy_rect.topright = (WIDTH - 10, 50)
                self.screen.blit(enemy_text, enemy_rect)
            
            # Draw game over or level complete message
            if self.game_over:
                try:
                    font_large = pygame.font.Font(None, 72)
                except:
                    font_large = pygame.font.SysFont('arial', 72)
                    
                text = font_large.render("GAME OVER", True, WHITE)
                rect = text.get_rect()
                rect.center = (WIDTH // 2, HEIGHT // 2)
                self.screen.blit(text, rect)
                
                text = font.render("Press R to retry or ESC to quit", True, WHITE)
                rect = text.get_rect()
                rect.center = (WIDTH // 2, HEIGHT // 2 + 50)
                self.screen.blit(text, rect)
            elif self.level_complete:
                try:
                    font_large = pygame.font.Font(None, 72)
                except:
                    font_large = pygame.font.SysFont('arial', 72)
                    
                text = font_large.render("LEVEL COMPLETE!", True, WHITE)
                rect = text.get_rect()
                rect.center = (WIDTH // 2, HEIGHT // 2)
                self.screen.blit(text, rect)
                
                text = font.render("Press ENTER to continue", True, WHITE)
                rect = text.get_rect()
                rect.center = (WIDTH // 2, HEIGHT // 2 + 50)
                self.screen.blit(text, rect)
        except Exception as e:
            print(f"Error drawing HUD: {e}")

    def _draw_debug_menu(self):
        """Draw the debug information overlay."""
        # Semi-transparent background
        debug_surface = pygame.Surface((300, 200))  # Reduced height since we removed 2 items
        debug_surface.fill((50, 50, 50))
        debug_surface.set_alpha(200)
        self.screen.blit(debug_surface, (10, 50))
        
        # Debug information
        font = pygame.font.Font(None, 24)
        y = 60
        debug_items = [
            "=== DEBUG MENU ===",
            f"Shields: {self.player.shields}",
            f"Spread Shot: {'ON' if self.player.spread_shot else 'OFF'}",
            f"Invincible: {self.debug_invincible}",
            f"Asteroids: {len(self.asteroids)}",
            f"Bullets: {len(self.bullets)}",
            f"Powerups: {len(self.powerups)}",
            "F3: Toggle Debug",
            "F4: Toggle Invincible",
            "F5: Skip Level",
            "F9: Toggle Spread Shot",
            "F10: Add Shield"
        ]
        
        for item in debug_items:
            text = font.render(item, True, WHITE)
            self.screen.blit(text, (20, y))
            y += 20

    def skip_level(self) -> None:
        """Skip to the next level by destroying all asteroids."""
        # Create explosions for all asteroids
        for asteroid in self.asteroids[:]:
            self.explosions.append(
                Explosion(asteroid.position[0], asteroid.position[1])
            )
            
            # Add score for each asteroid
            score_values = {
                'large': 20,
                'medium': 50,
                'small': 100
            }
            self.score += score_values[asteroid.size_name]
        
        # Clear all asteroids
        self.asteroids.clear()
        
        # Set level complete
        self.level_complete = True 