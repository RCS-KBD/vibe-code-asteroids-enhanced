import pygame
import sys
import random
import math
from pygame import Vector2

# Initialize Pygame
pygame.init()

# Constants
WIDTH = 800
HEIGHT = 600
FPS = 60
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SHIP_SIZE = 20
BULLET_SIZE = 3
BULLET_SPEED = 10
ASTEROID_SIZES = [50, 30, 20]

class Player:
    def __init__(self):
        self.position = Vector2(WIDTH // 2, HEIGHT // 2)
        self.velocity = Vector2(0, 0)
        self.acceleration = 0.5
        self.friction = 0.98
        self.rotation = 0
        self.size = 20

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

class Bullet:
    def __init__(self, x, y, angle):
        self.x = x
        self.y = y
        angle_rad = math.radians(angle)
        self.velocity_x = math.cos(angle_rad) * BULLET_SPEED
        self.velocity_y = -math.sin(angle_rad) * BULLET_SPEED
        self.lifetime = 60  # frames

    def update(self):
        self.x += self.velocity_x
        self.y += self.velocity_y
        self.x %= WIDTH
        self.y %= HEIGHT
        self.lifetime -= 1

    def draw(self, surface):
        pygame.draw.circle(surface, WHITE, (int(self.x), int(self.y)), BULLET_SIZE)

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

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Vibe Code Asteroids")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.asteroids = [Asteroid() for _ in range(4)]
        self.running = True
        self.bullets = []
        self.score = 0

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE:
                    # Create new bullet at ship's nose position with ship's angle
                    nose_x, nose_y = self.player.get_nose_position()
                    self.bullets.append(Bullet(nose_x, nose_y, self.player.rotation))

    def update(self):
        self.player.update()
        for asteroid in self.asteroids:
            asteroid.update()
        
        # Update bullets and remove dead ones
        self.bullets = [bullet for bullet in self.bullets if bullet.lifetime > 0]
        for bullet in self.bullets:
            bullet.update()

        # Collision detection
        for bullet in self.bullets[:]:
            for asteroid in self.asteroids[:]:
                dx = bullet.x - asteroid.x
                dy = bullet.y - asteroid.y
                distance = math.sqrt(dx**2 + dy**2)
                
                if distance < asteroid.size:
                    self.bullets.remove(bullet)
                    self.asteroids.remove(asteroid)
                    self.score += (3 - asteroid.size_index) * 100
                    
                    # Split asteroid if it's not the smallest size
                    if asteroid.size_index < len(ASTEROID_SIZES) - 1:
                        for _ in range(2):
                            self.asteroids.append(Asteroid(
                                asteroid.x, asteroid.y, 
                                asteroid.size_index + 1
                            ))
                    break

    def draw(self):
        self.screen.fill(BLACK)
        self.player.draw(self.screen)
        for bullet in self.bullets:
            bullet.draw(self.screen)
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
        
        # Draw score
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (10, 10))

        pygame.display.flip()

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