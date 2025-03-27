# Vibe Code Asteroids Enhanced

An enhanced version of the classic Asteroids game with modern features and improved architecture.

## Features

- Classic Asteroids gameplay with modern enhancements
- Enemy alien ships that hunt and shoot at the player
- Power-ups (shields and spread shot)
- Particle effects for explosions
- Sound effects with volume control
- Level progression system
- Score tracking
- Debug menu with cheat options

## Controls

- Arrow keys to move and rotate
- Space to shoot
- R to restart after game over
- Enter to continue to next level
- ESC to quit
- F3: Toggle Debug Menu
- F4: Toggle Invincibility (Debug)
- F5: Skip Level (Debug)
- F9: Toggle Spread Shot (Debug)
- F10: Add Shield (Debug)

## Project Structure

```
├── assets/
│   └── sounds/         # Game sound effects
├── src/
│   ├── entities/      # Game entities (player, asteroids, etc.)
│   ├── managers/      # Game systems (sound, collision, etc.)
│   └── utils/         # Utility functions and constants
├── main.py            # Game entry point
└── requirements.txt   # Python dependencies
```

## Installation

1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run the game: `python main.py`

## Contributing

Feel free to submit issues and enhancement requests!

## License

MIT License - feel free to use this code for your own projects!