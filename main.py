import pygame
import sys
import random
import math
from pygame import Vector2
from enum import Enum

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 1024
HEIGHT = 768
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 50, 50)
BLUE = (50, 50, 255)
YELLOW = (255, 255, 0)
SHIP_SIZE = 20
BULLET_SIZE = 3
BULLET_SPEED = 10
ENEMY_BULLET_SPEED = 5
ASTEROID_SIZES = [50, 30, 20]
POWERUP_SIZE = 15
POWERUP_DURATION = 900  # 15 seconds at 60 FPS
POWERUP_SPAWN_COOLDOWN = 1800  # 30 seconds at 60 FPS
ENEMY_SPAWN_DELAY = 300  # 5 seconds at 60 FPS

class PowerupType(Enum):
    SHIELD = 1
    SPREAD_SHOT = 2

class Powerup:
    def __init__(self, x, y, powerup_type, is_floating=False):
        self.position = Vector2(x, y)
        self.type = powerup_type
        self.size = POWERUP_SIZE
        self.angle = 0
        self.rotation_speed = 2
        self.collected = False
        self.is_floating = is_floating
        
        # Floating animation
        self.float_offset = 0
        self.float_speed = 0.1
        self.float_amplitude = 5
        
        # Movement for floating powerups
        if is_floating:
            # Start from either left or right side
            self.position.x = -POWERUP_SIZE if random.random() < 0.5 else WIDTH + POWERUP_SIZE
            self.position.y = random.randint(100, HEIGHT - 100)
            # Move in the opposite direction of where we spawned
            self.velocity = Vector2(2 if self.position.x < 0 else -2, 0)  # Increased base speed
            self.speed = 1  # Base movement speed

    def bounce_off_asteroid(self, asteroid_x, asteroid_y):
        # Calculate direction from asteroid to powerup
        direction = Vector2(self.position.x - asteroid_x, self.position.y - asteroid_y).normalize()
        # Reflect velocity based on collision normal
        self.velocity = direction * self.speed

    def update(self, asteroids):
        # Rotate the powerup
        self.angle = (self.angle + self.rotation_speed) % 360
        # Update floating animation
        self.float_offset = math.sin(pygame.time.get_ticks() * self.float_speed) * self.float_amplitude
        
        # Update position for floating powerups
        if self.is_floating:
            old_pos = Vector2(self.position)
            self.position += self.velocity * self.speed
            
            # Check for collision with asteroids
            for asteroid in asteroids:
                dx = self.position.x - asteroid.x
                dy = self.position.y - asteroid.y
                distance = math.sqrt(dx*dx + dy*dy)
                if distance < (self.size + asteroid.size):
                    # Restore position and bounce
                    self.position = old_pos
                    self.bounce_off_asteroid(asteroid.x, asteroid.y)
                    break
            
            # Screen wrapping
            if self.position.x < -self.size:
                self.position.x = WIDTH + self.size
            elif self.position.x > WIDTH + self.size:
                self.position.x = -self.size
            self.position.y = (self.position.y + self.velocity.y) % HEIGHT

    def draw(self, screen):
        if self.type == PowerupType.SHIELD:
            # Draw shield powerup (circle)
            pygame.draw.circle(screen, BLUE, 
                             (int(self.position.x), 
                              int(self.position.y + self.float_offset)), 
                             self.size, 1)
        else:
            # Draw spread shot powerup (triangle)
            points = []
            for i in range(3):
                angle = self.angle + i * 120
                point = self.position + Vector2(0, -self.size).rotate(angle)
                points.append(point)
            pygame.draw.polygon(screen, YELLOW, points, 1)

class Player:
    def __init__(self):
        self.position = Vector2(WIDTH // 2, HEIGHT // 2)
        self.velocity = Vector2(0, 0)
        self.acceleration = 0.5
        self.friction = 0.98
        self.rotation = 0
        self.size = 20
        self.shields = 0
        self.shield_angle = 0  # For rotating shield effect
        self.spread_shot = False
        self.spread_shot_timer = 0

    def get_nose_position(self):
        # Calculate the position of the ship's nose using Vector2
        nose_offset = Vector2(0, -self.size).rotate(self.rotation)
        return self.position + nose_offset

    def draw(self, screen):
        # Draw triangular ship
        points = [
            self.position + Vector2(0, -self.size).rotate(self.rotation),
            self.position + Vector2(-self.size/2, self.size/2).rotate(self.rotation),
            self.position + Vector2(self.size/2, self.size/2).rotate(self.rotation)
        ]
        pygame.draw.polygon(screen, WHITE, points, 2)
        
        # Draw shield bubble if shields are active
        if self.shields > 0:
            # Draw rotating shield bubble
            shield_radius = self.size + 10
            shield_points = []
            num_points = 20
            for i in range(num_points):
                angle = self.shield_angle + (i * 360 / num_points)
                point = self.position + Vector2(0, shield_radius).rotate(angle)
                shield_points.append(point)
            pygame.draw.polygon(screen, BLUE, shield_points, 1)
            
            # Draw shield count indicators below ship
            shield_spacing = 15
            for i in range(self.shields):
                pygame.draw.circle(screen, BLUE, 
                                 (int(self.position.x - self.size + (i * shield_spacing)), 
                                  int(self.position.y + self.size + 15)), 5, 1)
        
        # Draw spread shot indicator
        if self.spread_shot:
            pygame.draw.circle(screen, YELLOW,
                             (int(self.position.x), int(self.position.y + self.size + 15)), 5, 1)

    def update(self):
        keys = pygame.key.get_pressed()
        
        # Rotation
        if keys[pygame.K_LEFT]:
            self.rotation -= 5
        if keys[pygame.K_RIGHT]:
            self.rotation += 5

        # Thrust
        if keys[pygame.K_UP]:
            thrust = Vector2(0, -self.acceleration).rotate(self.rotation)
            self.velocity += thrust

        # Update position with velocity
        self.velocity *= self.friction
        self.position += self.velocity

        # Screen wrapping
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        
        # Update spread shot timer
        if self.spread_shot:
            self.spread_shot_timer -= 1
            if self.spread_shot_timer <= 0:
                self.spread_shot = False

        # Rotate shield bubble
        self.shield_angle = (self.shield_angle + 2) % 360

    def shoot(self):
        bullets = []
        nose_pos = self.get_nose_position()
        
        if self.spread_shot:
            # Create three bullets at different angles
            for angle_offset in [-20, 0, 20]:
                bullets.append(Bullet(nose_pos.x, nose_pos.y, self.rotation + angle_offset))
        else:
            # Create single bullet
            bullets.append(Bullet(nose_pos.x, nose_pos.y, self.rotation))
        
        return bullets

class Bullet:
    def __init__(self, x, y, angle):
        self.position = Vector2(x, y)
        # Use the same Vector2 direction calculation as the ship's nose
        self.velocity = Vector2(0, -BULLET_SPEED).rotate(angle)
        self.lifetime = 60  # frames

    def update(self):
        self.position += self.velocity
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        self.lifetime -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.position.x), int(self.position.y)), BULLET_SIZE)

class Asteroid:
    def __init__(self, x=None, y=None, size_index=0):
        self.size_index = size_index
        self.size = ASTEROID_SIZES[size_index]
        if x is None:
            self.x = random.randint(0, WIDTH)
        else:
            self.x = x
        if y is None:
            self.y = random.randint(0, HEIGHT)
        else:
            self.y = y
        
        angle = random.random() * 2 * math.pi
        speed = random.random() * 2 + 1
        self.velocity_x = math.cos(angle) * speed
        self.velocity_y = math.sin(angle) * speed

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, (int(self.x), int(self.y)), self.size, 2)

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.x %= WIDTH
        self.y %= HEIGHT

class ExplosionLine:
    def __init__(self, x, y, angle):
        self.position = Vector2(x, y)
        self.velocity = Vector2(0, -5).rotate(angle)  # Lines shoot out at different angles
        self.lifetime = 30  # frames
        self.length = 20  # pixels

    def update(self):
        self.position += self.velocity
        self.lifetime -= 1

    def draw(self, surface):
        if self.lifetime > 0:
            # Calculate end point of the line
            end_pos = self.position + self.velocity.normalize() * self.length
            # Fade out the line as lifetime decreases
            alpha = int((self.lifetime / 30) * 255)
            color = (255, 255, 255, alpha)
            pygame.draw.line(surface, color, 
                           (int(self.position.x), int(self.position.y)),
                           (int(end_pos.x), int(end_pos.y)), 2)

class EnemyBullet:
    def __init__(self, x, y, target_pos):
        self.position = Vector2(x, y)
        # Calculate direction to target
        direction = Vector2(target_pos.x - x, target_pos.y - y).normalize()
        self.velocity = direction * ENEMY_BULLET_SPEED
        self.lifetime = 120  # Slower bullets live longer

    def update(self):
        self.position += self.velocity
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        self.lifetime -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, RED, (int(self.position.x), int(self.position.y)), BULLET_SIZE)

class EnemyShip:
    def __init__(self, is_boss=False):
        # Start from a random edge
        if random.random() < 0.5:
            self.position = Vector2(random.choice([0, WIDTH]), random.randint(0, HEIGHT))
        else:
            self.position = Vector2(random.randint(0, WIDTH), random.choice([0, HEIGHT]))
        
        self.velocity = Vector2(0, 0)
        self.is_boss = is_boss
        
        # Boss has enhanced stats
        if is_boss:
            self.size = 35  # Bigger
            self.shoot_cooldown = 60  # Faster shooting
            self.speed = 2.5  # Faster movement
            self.health = 3  # More health
        else:
            self.size = 25
            self.shoot_cooldown = 120  # Slower shooting for regular enemy
            self.speed = 1.5  # Slower movement
            self.health = 1  # One hit kill
        
        self.current_cooldown = 0

    def update(self, player_pos):
        # Move towards player with some randomness
        direction = Vector2(player_pos.x - self.position.x, 
                          player_pos.y - self.position.y).normalize()
        # Add slight randomness to movement
        direction.rotate_ip(random.uniform(-15, 15))
        
        # Keep distance from player (don't get too close)
        distance_to_player = self.position.distance_to(player_pos)
        if distance_to_player < (300 if self.is_boss else 200):
            direction = -direction
        
        # Update velocity and position
        self.velocity = direction * self.speed
        self.position += self.velocity
        self.position.x %= WIDTH
        self.position.y %= HEIGHT
        
        # Update shooting cooldown
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def can_shoot(self):
        return self.current_cooldown <= 0

    def shoot(self, target_pos):
        self.current_cooldown = self.shoot_cooldown
        return EnemyBullet(self.position.x, self.position.y, target_pos)

    def draw(self, screen):
        # Draw enemy ship as a diamond shape
        points = [
            (self.position.x, self.position.y - self.size),
            (self.position.x + self.size, self.position.y),
            (self.position.x, self.position.y + self.size),
            (self.position.x - self.size, self.position.y)
        ]
        color = RED if not self.is_boss else (255, 0, 0)  # Brighter red for boss
        pygame.draw.polygon(screen, color, points, 3 if self.is_boss else 2)
        
        # Draw health indicator
        for i in range(self.health):
            pygame.draw.circle(screen, color, 
                             (int(self.position.x - self.size + 10 + i * 10), 
                              int(self.position.y - self.size - 10)), 3)

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Vibe Code Asteroids")
        self.clock = pygame.time.Clock()
        self.show_debug = False
        self.debug_invincible = False  # Debug invincibility
        self.debug_spread_shot = False  # Debug spread shot
        self.invincible = False
        self.paused = False
        self.powerups = []
        self.floating_powerup_timer = POWERUP_SPAWN_COOLDOWN
        self.powerup_spawn_timers = {
            PowerupType.SHIELD: 0,
            PowerupType.SPREAD_SHOT: 0
        }
        self.enemy_spawn_timer = ENEMY_SPAWN_DELAY
        self.enemies_remaining = 0
        self.reset_game()

    def reset_game(self):
        self.player = Player()
        self.level = 1
        self.enemy = None
        self.enemy_bullets = []
        self.powerups = []
        self.enemies_remaining = 0
        self.enemy_spawn_timer = ENEMY_SPAWN_DELAY
        self.start_new_level()
        self.running = True
        self.game_over = False
        self.level_complete = False
        self.level_transition_timer = 0
        self.bullets = []
        self.score = 0
        self.explosion_lines = []

    def get_safe_asteroid_position(self):
        # Keep asteroids away from the center (player spawn)
        center_x, center_y = WIDTH // 2, HEIGHT // 2
        safe_radius = 100  # Minimum distance from center
        
        # Choose a random edge of the screen to spawn from
        if random.random() < 0.5:
            # Spawn on left or right edge
            x = random.choice([random.randint(0, 100), random.randint(WIDTH-100, WIDTH)])
            y = random.randint(0, HEIGHT)
        else:
            # Spawn on top or bottom edge
            x = random.randint(0, WIDTH)
            y = random.choice([random.randint(0, 100), random.randint(HEIGHT-100, HEIGHT)])
        
        return x, y

    def start_new_level(self):
        # Clear any remaining objects
        self.asteroids = []
        self.bullets = []
        self.enemy_bullets = []
        self.enemy = None
        
        # Set up enemies for level 2
        if self.level == 2:
            self.enemies_remaining = 2
            self.enemy_spawn_timer = ENEMY_SPAWN_DELAY
        elif self.level == 3:
            self.enemies_remaining = 1
            self.enemy_spawn_timer = ENEMY_SPAWN_DELAY
            self.enemy = EnemyShip(is_boss=True)
        else:
            self.enemies_remaining = 0
        
        # Number of asteroids increases with each level
        if self.level == 3:
            num_asteroids = 2  # Minimal asteroids in boss fight
        else:
            num_asteroids = 3 + self.level
        
        # Create new asteroids
        for _ in range(num_asteroids):
            x, y = self.get_safe_asteroid_position()
            asteroid = Asteroid(x, y)
            speed_multiplier = 1 + (self.level - 1) * 0.1
            asteroid.velocity_x *= speed_multiplier
            asteroid.velocity_y *= speed_multiplier
            self.asteroids.append(asteroid)
        
        self.level_complete = False
        self.level_transition_timer = 0

    def check_level_complete(self):
        if len(self.asteroids) == 0 and (self.enemy is None or self.enemy.health <= 0) and not self.level_complete:
            self.level_complete = True
            self.level_transition_timer = 180  # 3 seconds at 60 FPS

    def create_explosion(self, x, y):
        # Create 12 lines shooting out in different directions
        for i in range(12):
            angle = i * 30  # 360 degrees / 12 = 30 degrees between each line
            self.explosion_lines.append(ExplosionLine(x, y, angle))

    def spawn_powerup(self, x, y, from_enemy=False, from_large_asteroid=False):
        if from_enemy:
            # Always spawn shield from defeated enemies if player has no shields
            if self.player.shields == 0:
                self.powerups.append(Powerup(x, y, PowerupType.SHIELD))
        elif from_large_asteroid:
            # Only spawn shield if player has no shields and 10% chance
            if self.player.shields == 0 and random.random() < 0.1:
                self.powerups.append(Powerup(x, y, PowerupType.SHIELD))
        else:
            # Floating powerups are always spread shot
            self.powerups.append(Powerup(x, y, PowerupType.SPREAD_SHOT, is_floating=True))

    def check_player_asteroid_collision(self):
        # Check collision between player and asteroids
        for asteroid in self.asteroids[:]:
            dx = self.player.position.x - asteroid.x
            dy = self.player.position.y - asteroid.y
            distance = math.sqrt(dx**2 + dy**2)
            
            if distance < (self.player.size/2 + asteroid.size):
                if self.invincible:
                    self.asteroids.remove(asteroid)
                    self.score += (3 - asteroid.size_index) * 100
                    self.create_explosion(asteroid.x, asteroid.y)
                    # Only spawn shield from large asteroids when invincible
                    if asteroid.size_index == 0:
                        self.spawn_powerup(asteroid.x, asteroid.y, from_large_asteroid=True)
                elif self.player.shields > 0:
                    # Use up a shield instead of dying
                    self.player.shields -= 1
                    self.asteroids.remove(asteroid)
                    self.create_explosion(asteroid.x, asteroid.y)
                    # Don't spawn shield when using a shield
                else:
                    self.game_over = True
                    self.create_explosion(self.player.position.x, self.player.position.y)
                break

    def update(self):
        if self.paused:
            return

        if self.game_over:
            self.explosion_lines = [line for line in self.explosion_lines if line.lifetime > 0]
            for line in self.explosion_lines:
                line.update()
            return

        if self.level_complete:
            self.level_transition_timer -= 1
            if self.level_transition_timer <= 0:
                self.level += 1
                self.start_new_level()
            return

        # Handle enemy spawning in level 2
        if self.level == 2 and self.enemies_remaining > 0 and not self.enemy:
            self.enemy_spawn_timer -= 1
            if self.enemy_spawn_timer <= 0:
                self.enemy = EnemyShip(is_boss=False)
                self.enemy_spawn_timer = ENEMY_SPAWN_DELAY  # Reset for next enemy

        # Update powerup spawn cooldowns
        for ptype in self.powerup_spawn_timers:
            if self.powerup_spawn_timers[ptype] > 0:
                self.powerup_spawn_timers[ptype] -= 1

        # Spawn floating spread shot powerups periodically
        self.floating_powerup_timer -= 1
        if self.floating_powerup_timer <= 0 and self.powerup_spawn_timers[PowerupType.SPREAD_SHOT] <= 0:
            self.spawn_powerup(0, 0, False, False)
            self.floating_powerup_timer = POWERUP_SPAWN_COOLDOWN
            self.powerup_spawn_timers[PowerupType.SPREAD_SHOT] = POWERUP_SPAWN_COOLDOWN

        self.player.update()
        
        # Update and clean up powerups
        self.powerups = [p for p in self.powerups if not p.collected]
        for powerup in self.powerups:
            powerup.update(self.asteroids)  # Pass asteroids for collision checking
            # Check for collision with player
            dx = powerup.position.x - self.player.position.x
            dy = powerup.position.y - self.player.position.y
            if math.sqrt(dx*dx + dy*dy) < (self.player.size + powerup.size):
                if powerup.type == PowerupType.SHIELD:
                    self.player.shields += 1
                else:  # SPREAD_SHOT
                    self.player.spread_shot = True
                    self.player.spread_shot_timer = POWERUP_DURATION
                powerup.collected = True

        for asteroid in self.asteroids:
            asteroid.update()
        
        # Update enemy ship and bullets
        if self.enemy and self.enemy.health > 0:
            self.enemy.update(self.player.position)
            
            # Check for ship collision
            dx = self.enemy.position.x - self.player.position.x
            dy = self.enemy.position.y - self.player.position.y
            distance = math.sqrt(dx*dx + dy*dy)
            if distance < (self.player.size + self.enemy.size):
                if self.invincible:
                    # Destroy enemy ship on collision if invincible
                    self.enemy.health = 0
                    self.score += 1000 if self.enemy.is_boss else 500
                    self.create_explosion(self.enemy.position.x, self.enemy.position.y)
                    if self.level == 2:
                        self.enemies_remaining -= 1
                        self.spawn_powerup(self.enemy.position.x, self.enemy.position.y, from_enemy=True)
                        self.enemy = None
                else:
                    # Player dies on collision if not invincible
                    self.game_over = True
                    self.create_explosion(self.player.position.x, self.player.position.y)
            
            if self.enemy.can_shoot():
                self.enemy_bullets.append(self.enemy.shoot(self.player.position))
        
        # Update enemy bullets
        self.enemy_bullets = [bullet for bullet in self.enemy_bullets if bullet.lifetime > 0]
        for bullet in self.enemy_bullets:
            bullet.update()
            
            # Check if enemy bullet hits player
            dx = bullet.position.x - self.player.position.x
            dy = bullet.position.y - self.player.position.y
            if not self.invincible and math.sqrt(dx*dx + dy*dy) < self.player.size:
                self.game_over = True
                self.create_explosion(self.player.position.x, self.player.position.y)
                break
        
        # Update player bullets
        self.bullets = [bullet for bullet in self.bullets if bullet.lifetime > 0]
        for bullet in self.bullets:
            bullet.update()
            
            # Check if bullet hits enemy ship
            if self.enemy and self.enemy.health > 0:
                dx = bullet.position.x - self.enemy.position.x
                dy = bullet.position.y - self.enemy.position.y
                if math.sqrt(dx*dx + dy*dy) < self.enemy.size:
                    self.enemy.health -= 1
                    self.bullets.remove(bullet)
                    if self.enemy.health <= 0:
                        self.score += 1000 if self.enemy.is_boss else 500
                        self.create_explosion(self.enemy.position.x, self.enemy.position.y)
                        if self.level == 2:
                            self.enemies_remaining -= 1
                            self.spawn_powerup(self.enemy.position.x, self.enemy.position.y, from_enemy=True)
                            self.enemy = None
                    break

        # Check for player collision with asteroids
        self.check_player_asteroid_collision()

        # Bullet-asteroid collision detection
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                dx = bullet.position.x - asteroid.x
                dy = bullet.position.y - asteroid.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < asteroid.size:
                    if bullet in self.bullets:  # Check if bullet still exists
                        self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += (3 - asteroid.size_index) * 100
                    
                    # Only spawn powerups from large asteroids (size_index 0)
                    if asteroid.size_index == 0:
                        self.spawn_powerup(asteroid.x, asteroid.y, from_large_asteroid=True)
                    
                    # Split asteroid if it's not the smallest size
                    if asteroid.size_index < len(ASTEROID_SIZES) - 1:
                        for _ in range(2):
                            new_asteroid = Asteroid(
                                asteroid.x, asteroid.y, 
                                asteroid.size_index + 1
                            )
                            # Apply same level speed multiplier
                            speed_multiplier = 1 + (self.level - 1) * 0.1
                            new_asteroid.velocity_x *= speed_multiplier
                            new_asteroid.velocity_y *= speed_multiplier
                            self.asteroids.append(new_asteroid)
                    break

        # Check if level is complete
        self.check_level_complete()

        # Update explosion lines
        self.explosion_lines = [line for line in self.explosion_lines if line.lifetime > 0]
        for line in self.explosion_lines:
            line.update()

    def draw_debug_menu(self):
        if not self.show_debug:
            return

        # Semi-transparent background for debug menu
        debug_surface = pygame.Surface((300, 250))  # Made taller for more options
        debug_surface.fill((50, 50, 50))
        debug_surface.set_alpha(200)
        self.screen.blit(debug_surface, (10, 50))

        font = pygame.font.Font(None, 24)
        y = 60
        debug_items = [
            "=== DEBUG MENU ===",
            f"FPS: {int(self.clock.get_fps())}",
            f"Asteroids: {len(self.asteroids)}",
            f"Bullets: {len(self.bullets)}",
            f"Player Shields: {self.player.shields}",
            f"Spread Shot: {'ON' if self.player.spread_shot else 'OFF'}",
            "F3: Toggle Debug",
            "F4: Toggle Invincible",
            "F5: Skip Level",
            "F6: Previous Level",
            "F7: Next Level",
            "F8: Clear Asteroids",
            "F9: Toggle Spread Shot",
            "F10: Add Shield"
        ]

        for item in debug_items:
            text = font.render(item, True, WHITE)
            self.screen.blit(text, (20, y))
            y += 20

    def draw_pause_menu(self):
        if not self.paused:
            return

        # Semi-transparent overlay
        pause_overlay = pygame.Surface((WIDTH, HEIGHT))
        pause_overlay.fill((0, 0, 0))
        pause_overlay.set_alpha(128)
        self.screen.blit(pause_overlay, (0, 0))

        # Pause menu text
        font_large = pygame.font.Font(None, 74)
        font = pygame.font.Font(None, 36)
        
        pause_text = font_large.render("PAUSED", True, WHITE)
        text_rect = pause_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
        self.screen.blit(pause_text, text_rect)
        
        controls_text = font.render("Press P to Resume", True, WHITE)
        controls_rect = controls_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 20))
        self.screen.blit(controls_text, controls_rect)
        
        quit_text = font.render("Press ESC to Quit", True, WHITE)
        quit_rect = quit_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 60))
        self.screen.blit(quit_text, quit_rect)

    def draw(self):
        self.screen.fill(BLACK)
        
        # Draw powerups
        for powerup in self.powerups:
            powerup.draw(self.screen)
        
        # Draw game objects
        if not self.game_over:
            self.player.draw(self.screen)
            if self.invincible:
                pygame.draw.circle(self.screen, WHITE, 
                                 (int(self.player.position.x), int(self.player.position.y)), 
                                 self.player.size + 5, 1)
            
            # Draw spread shot timer if active
            if self.player.spread_shot:
                remaining_time = self.player.spread_shot_timer / FPS
                timer_text = f"{int(remaining_time)}s"
                font = pygame.font.Font(None, 24)
                text = font.render(timer_text, True, YELLOW)
                text_rect = text.get_rect(center=(self.player.position.x, 
                                                self.player.position.y + self.player.size + 30))
                self.screen.blit(text, text_rect)
        
        # Draw enemy ship and bullets
        if self.enemy and self.enemy.health > 0:
            self.enemy.draw(self.screen)
        for bullet in self.enemy_bullets:
            bullet.draw(self.screen)
        
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Draw explosion lines
        for line in self.explosion_lines:
            line.draw(self.screen)

        # Draw HUD
        font = pygame.font.Font(None, 36)
        # Draw score in top left
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))
        # Draw level in top right
        level_text = font.render(f"Level: {self.level}", True, WHITE)
        level_rect = level_text.get_rect()
        level_rect.topright = (WIDTH - 10, 10)
        self.screen.blit(level_text, level_rect)

        # Draw level complete message
        if self.level_complete and not self.game_over:
            font_large = pygame.font.Font(None, 74)
            level_complete_text = font_large.render(f"Level {self.level} Complete!", True, WHITE)
            text_rect = level_complete_text.get_rect(center=(WIDTH/2, HEIGHT/2 - 50))
            self.screen.blit(level_complete_text, text_rect)
            
            font = pygame.font.Font(None, 48)
            next_level_text = font.render(f"Get Ready for Level {self.level + 1}", True, WHITE)
            next_rect = next_level_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
            self.screen.blit(next_level_text, next_rect)

        # Draw game over message
        if self.game_over:
            font = pygame.font.Font(None, 74)
            game_over_text = font.render("GAME OVER", True, WHITE)
            text_rect = game_over_text.get_rect(center=(WIDTH/2, HEIGHT/2))
            self.screen.blit(game_over_text, text_rect)
            
            font = pygame.font.Font(None, 36)
            final_score_text = font.render(f"Final Score: {self.score}", True, WHITE)
            score_rect = final_score_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 50))
            self.screen.blit(final_score_text, score_rect)
            
            restart_text = font.render("Press R to Restart or ESC to Quit", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH/2, HEIGHT/2 + 100))
            self.screen.blit(restart_text, restart_rect)

        # Draw enemy ships remaining (if in level 2 or 3)
        if self.level >= 2:
            font = pygame.font.Font(None, 36)
            if self.level == 2:
                enemy_text = f"Enemy Ships: {self.enemies_remaining}"
            else:
                enemy_text = "BOSS" if self.enemy and self.enemy.health > 0 else ""
            text = font.render(enemy_text, True, RED)
            text_rect = text.get_rect(center=(WIDTH/2, 30))
            self.screen.blit(text, text_rect)

        # Draw debug menu last so it overlays everything else
        self.draw_debug_menu()
        
        # Draw pause menu over everything
        self.draw_pause_menu()

        pygame.display.flip()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if self.paused:
                        self.running = False
                    else:
                        self.paused = True
                elif event.key == pygame.K_p:
                    self.paused = not self.paused
                elif event.key == pygame.K_SPACE and not self.game_over and not self.level_complete and not self.paused:
                    # Use player's shoot method which handles spread shot
                    self.bullets.extend(self.player.shoot())
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()
                elif event.key == pygame.K_F3:
                    self.show_debug = not self.show_debug
                elif event.key == pygame.K_F4 and self.show_debug:
                    self.debug_invincible = not self.debug_invincible
                    self.invincible = self.debug_invincible
                elif event.key == pygame.K_F5 and self.show_debug:
                    self.level_complete = True
                    self.level_transition_timer = 120
                elif event.key == pygame.K_F6 and self.show_debug:
                    self.level = max(1, self.level - 1)
                    self.start_new_level()
                elif event.key == pygame.K_F7 and self.show_debug:
                    self.level += 1
                    self.start_new_level()
                elif event.key == pygame.K_F8 and self.show_debug:
                    self.asteroids.clear()
                elif event.key == pygame.K_F9 and self.show_debug:
                    self.debug_spread_shot = not self.debug_spread_shot
                    self.player.spread_shot = self.debug_spread_shot
                    if self.player.spread_shot:
                        self.player.spread_shot_timer = POWERUP_DURATION
                elif event.key == pygame.K_F10 and self.show_debug:
                    self.player.shields += 1

    def run(self):
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

if __name__ == "__main__":
    game = Game()
    game.run()
    pygame.quit()
    sys.exit()