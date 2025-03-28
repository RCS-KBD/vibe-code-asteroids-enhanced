# Contributing Guidelines

## Development Workflow

### 1. Testing Protocol
- All changes must be tested locally before committing
- Testing sequence:
  1. Run game to verify basic functionality
  2. Test the specific feature/change that was modified
  3. Test related features to ensure no regressions
- Document test results in commit messages

### 2. Code Preservation
- Never delete existing working code without explicit confirmation
- Use comments to temporarily disable code rather than deleting when testing alternatives
- Keep original function signatures and parameters intact
- Document any API changes before implementation

### 3. Python/Pygame Best Practices
- Follow PEP 8 style guidelines
- Use type hints for all functions and methods
- Maintain existing class structure patterns
- Keep Pygame-specific code in appropriate modules

## Example Commit Message
```
feat(enemy): Add new movement pattern

- Added oscillating movement to enemy ships
- Tested:
  * Basic game functionality ✓
  * New movement pattern ✓
  * Collision detection with new pattern ✓
  * No impact on existing features ✓
```

## Code Style Example
```python
def update_movement(self, delta_time: float) -> None:
    """Update enemy movement pattern.
    
    Args:
        delta_time: Time since last frame in seconds
    """
    # Implementation
    pass
``` 