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

class Player:
    def __init__(self):
        self.position = Vector2(WIDTH // 2, HEIGHT // 2)
        self.velocity = Vector2(0, 0)
        self.acceleration = 0.5
        self.friction = 0.98
        self.rotation = 0
        self.size = 20

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

class Asteroid:
    def __init__(self, size=3):
        self.size = size
        self.radius = size * 20
        self.position = Vector2(
            random.randrange(WIDTH),
            random.randrange(HEIGHT)
        )
        self.velocity = Vector2(
            random.random() * 2 - 1,
            random.random() * 2 - 1
        )
        self.rotation = 0
        self.rotation_speed = random.random() * 2 - 1

    def draw(self, screen):
        pygame.draw.circle(screen, WHITE, self.position, self.radius, 2)

    def update(self):
        self.position += self.velocity
        self.rotation += self.rotation_speed

        # Screen wrapping
        self.position.x %= WIDTH
        self.position.y %= HEIGHT

class Game:
    def __init__(self):
        self.screen = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption("Vibe Code Asteroids")
        self.clock = pygame.time.Clock()
        self.player = Player()
        self.asteroids = [Asteroid() for _ in range(4)]
        self.running = True

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False

    def update(self):
        self.player.update()
        for asteroid in self.asteroids:
            asteroid.update()

    def draw(self):
        self.screen.fill(BLACK)
        self.player.draw(self.screen)
        for asteroid in self.asteroids:
            asteroid.draw(self.screen)
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