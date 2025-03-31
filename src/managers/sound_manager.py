import os
import pygame
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds: Dict[str, Optional[pygame.mixer.Sound]] = {}
        self._load_sounds()
        
    def _load_sounds(self):
        """Load all sound effects."""
        sound_files = {
            'shoot': ['laserSmall_000.ogg', 'shoot.wav'],
            'explosion': ['explosionCrunch_000.ogg', 'explosion.wav'],
            'shield': ['forceField_000.ogg', 'shield.wav'],
            'hit': ['impactMetal_000.ogg', 'hit.wav'],
            'powerup': ['computerNoise_000.ogg', 'powerup.wav'],
            'thrust': ['thrusterFire_000.ogg', 'thrust.wav']
        }
        
        for sound_name, filenames in sound_files.items():
            self.sounds[sound_name] = None
            for filename in filenames:
                try:
                    path = os.path.join('assets', 'sounds', filename)
                    if os.path.exists(path):
                        self.sounds[sound_name] = pygame.mixer.Sound(path)
                        logger.info(f"Loaded sound: {sound_name} from {filename}")
                        break
                except Exception as e:
                    logger.warning(f"Could not load sound file: {filename}")
                    continue
            
            if self.sounds[sound_name] is None:
                logger.warning(f"No sound file found for: {sound_name}")
    
    def play(self, sound_name: str):
        """Play a sound effect."""
        if sound := self.sounds.get(sound_name):
            try:
                sound.play()
            except Exception as e:
                logger.warning(f"Could not play sound: {sound_name}")
        else:
            logger.warning(f"Sound not found: {sound_name}")
    
    def stop(self, sound_name: str):
        """Stop a sound effect."""
        if sound := self.sounds.get(sound_name):
            try:
                sound.stop()
            except Exception as e:
                logger.warning(f"Could not stop sound: {sound_name}")