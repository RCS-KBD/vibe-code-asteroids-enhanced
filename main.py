"""Main game module."""

import sys
import pygame
from src.utils.constants import WIDTH, HEIGHT, FPS, BLACK
from src.utils.logging_config import setup_logging
from src.managers.game_manager import GameManager
from src.managers.sound_manager import SoundManager

def main():
    """Main game function."""
    # Initialize logging
    setup_logging()

    # Initialize Pygame
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Vibe Code Asteroids")
    clock = pygame.time.Clock()

    # Initialize managers
    sound_manager = SoundManager()
    game_manager = GameManager(screen, sound_manager)

    # Main game loop
    running = True
    while running:
        # Handle events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_RETURN and game_manager.level_complete:
                    game_manager.start_next_level()
                elif event.key == pygame.K_r and game_manager.game_over:
                    game_manager.reset_game()
                elif event.key == pygame.K_SPACE:
                    game_manager.shoot()
                elif event.key == pygame.K_F3:
                    game_manager.show_debug = not game_manager.show_debug
                elif event.key == pygame.K_F4:
                    game_manager.debug_invincible = not game_manager.debug_invincible
                    game_manager.player.is_invulnerable = game_manager.debug_invincible
                elif event.key == pygame.K_F5:
                    game_manager.skip_level()
                elif event.key == pygame.K_F9:
                    game_manager.player.activate_spread_shot()
                elif event.key == pygame.K_F10:
                    game_manager.player.add_shield()

        # Update game state
        game_manager.update()
        
        # Draw everything
        screen.fill(BLACK)
        game_manager.draw()
        pygame.display.flip()

        # Cap the frame rate
        clock.tick(FPS)

    # Clean up
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()