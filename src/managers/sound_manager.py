"""Sound manager module."""

import os
import pygame
import logging
from typing import Dict

class SoundManager:
    """Manages loading and playing game sounds."""
    
    def __init__(self):
        """Initialize the sound manager."""
        self.logger = logging.getLogger(__name__)
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        
        # Initialize pygame mixer
        try:
            pygame.mixer.init()
            self._load_sound_effects()
        except pygame.error as e:
            self.logger.error(f"Failed to initialize sound system: {e}")
    
    def _load_sound_effects(self):
        """Load all sound effects."""
        try:
            # Map of sound names to filenames
            sound_files = {
                'shoot': 'laserSmall_000.ogg',
                'explosion': 'explosionCrunch_000.ogg',
                'powerup': 'forceField_000.ogg',
                'shield_hit': 'impactMetal_000.ogg',
                'level_complete': 'computerNoise_000.ogg',
                'thrust': 'thrusterFire_000.ogg'  # Added thrust sound
            }
            
            # Load each sound file
            for name, filename in sound_files.items():
                path = os.path.join('assets', 'sounds', filename)
                if os.path.exists(path):
                    self.sounds[name] = pygame.mixer.Sound(path)
                    # Set specific volumes
                    if name == 'level_complete':
                        self.sounds[name].set_volume(0.3)  # Reduce level complete volume
                    elif name == 'thrust':
                        self.sounds[name].set_volume(0.4)  # Keep thrust sound quieter
                    else:
                        self.sounds[name].set_volume(0.5)  # Default volume for other sounds
                else:
                    self.logger.warning(f"Sound file not found: {path}")
        except pygame.error as e:
            self.logger.error(f"Error loading sound effects: {e}")
    
    def play(self, sound_name: str) -> None:
        """Play a sound effect.
        
        Args:
            sound_name: Name of the sound to play
        """
        if sound_name in self.sounds:
            try:
                if sound_name == 'level_complete':
                    # Stop the sound after 2 seconds
                    self.sounds[sound_name].play(maxtime=2000)  # 2000 milliseconds = 2 seconds
                else:
                    self.sounds[sound_name].play()
            except pygame.error as e:
                self.logger.error(f"Error playing sound {sound_name}: {e}")
        else:
            self.logger.warning(f"Sound not found: {sound_name}")
    
    def stop(self, name: str) -> None:
        """Stop a playing sound effect.
        
        Args:
            name: Name of the sound to stop
        """
        if name in self.sounds:
            try:
                self.sounds[name].stop()
            except pygame.error as e:
                self.logger.error(f"Failed to stop sound '{name}': {e}")
        else:
            self.logger.warning(f"Unknown sound: {name}")
    
    def stop_all(self) -> None:
        """Stop all playing sounds."""
        try:
            pygame.mixer.stop()
        except pygame.error as e:
            self.logger.error(f"Failed to stop all sounds: {e}")
    
    def set_volume(self, name: str, volume: float) -> None:
        """Set the volume for a specific sound.
        
        Args:
            name: Name of the sound
            volume: Volume level (0.0 to 1.0)
        """
        if name in self.sounds:
            try:
                self.sounds[name].set_volume(max(0.0, min(1.0, volume)))
            except pygame.error as e:
                self.logger.error(f"Failed to set volume for '{name}': {e}")
        else:
            self.logger.warning(f"Unknown sound: {name}") 