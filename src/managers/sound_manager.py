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
            'shoot': 'laserSmall_000.ogg',
            'explosion': 'explosionCrunch_000.ogg',
            'shield': 'forceField_000.ogg',
            'hit': 'impactMetal_000.ogg',
            'powerup': 'impactMetal_003.ogg',
            'thrust': 'thrusterFire_000.ogg',
            'shield_hit': 'forceField_000.ogg'
        }
        
        for sound_name, filename in sound_files.items():
            self.sounds[sound_name] = None
            try:
                path = os.path.join('assets', 'sounds', filename)
                if os.path.exists(path):
                    self.sounds[sound_name] = pygame.mixer.Sound(path)
                    logger.info(f"Loaded sound: {sound_name} from {filename}")
                else:
                    logger.warning(f"Sound file not found: {filename}")
            except Exception as e:
                logger.warning(f"Could not load sound file: {filename}")
    
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