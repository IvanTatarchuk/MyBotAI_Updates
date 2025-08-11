#!/usr/bin/env python3
"""
Mobile Game Builder - Call of Duty Mobile Style
Advanced mobile game development system
"""

import os
import json
import subprocess
from pathlib import Path
from typing import Dict, Any, List

class MobileGameBuilder:
    """Mobile game builder for creating Call of Duty Mobile style games."""
    
    def __init__(self):
        self.frameworks = ['kivy', 'pygame', 'unity_python', 'custom_engine']
        self.platforms = ['android', 'ios']
        
    def create_mobile_game(self, game_name: str, framework: str = 'kivy', 
                          platform: str = 'android') -> Dict[str, Any]:
        """Create a complete mobile game project."""
        
        if framework not in self.frameworks:
            raise ValueError(f"Unsupported framework: {framework}")
        
        if platform not in self.platforms:
            raise ValueError(f"Unsupported platform: {platform}")
        
        project_structure = {
            'name': game_name,
            'framework': framework,
            'platform': platform,
            'directories': self._create_directories(game_name),
            'files': self._create_files(game_name, framework, platform),
            'dependencies': self._get_dependencies(framework),
            'build_config': self._create_build_config(game_name, framework, platform)
        }
        
        return project_structure
    
    def _create_directories(self, game_name: str) -> List[str]:
        """Create project directory structure."""
        return [
            f"{game_name}/",
            f"{game_name}/src/",
            f"{game_name}/src/core/",
            f"{game_name}/src/gameplay/",
            f"{game_name}/src/graphics/",
            f"{game_name}/src/audio/",
            f"{game_name}/src/ui/",
            f"{game_name}/assets/",
            f"{game_name}/assets/models/",
            f"{game_name}/assets/textures/",
            f"{game_name}/assets/sounds/",
            f"{game_name}/assets/maps/",
            f"{game_name}/config/",
            f"{game_name}/build/",
            f"{game_name}/docs/"
        ]
    
    def _create_files(self, game_name: str, framework: str, platform: str) -> Dict[str, str]:
        """Create essential game files."""
        files = {}
        
        # Main game file
        files[f"{game_name}/main.py"] = self._generate_main_file(game_name, framework)
        
        # Framework-specific files
        if framework == 'kivy':
            files.update(self._create_kivy_files(game_name, platform))
        elif framework == 'pygame':
            files.update(self._create_pygame_files(game_name, platform))
        
        # Common game files
        files[f"{game_name}/game_config.json"] = self._generate_game_config(game_name)
        files[f"{game_name}/requirements.txt"] = self._generate_requirements(framework)
        
        return files
    
    def _generate_main_file(self, game_name: str, framework: str) -> str:
        """Generate main game file."""
        if framework == 'kivy':
            return self._generate_kivy_main(game_name)
        elif framework == 'pygame':
            return self._generate_pygame_main(game_name)
        else:
            return self._generate_generic_main(game_name)
    
    def _generate_kivy_main(self, game_name: str) -> str:
        """Generate Kivy main file."""
        return f'''#!/usr/bin/env python3
"""
{game_name} - Mobile FPS Game with Kivy
"""

from kivy.app import App
from kivy.uix.widget import Widget
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.graphics import Color, Rectangle, Line
from kivy.uix.screenmanager import ScreenManager, Screen
import math
import random

class GameScreen(Screen):
    """Main game screen."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.score = 0
        self.health = 100
        self.enemies = []
        self.bullets = []
        
        # Setup UI
        self.setup_ui()
        
        # Start game loop
        Clock.schedule_interval(self.update, 1.0/60.0)
    
    def setup_ui(self):
        """Setup game UI."""
        layout = FloatLayout()
        
        # HUD
        self.health_label = Label(
            text=f'Health: {{self.health}}',
            pos_hint={{'x': 0.05, 'y': 0.9}},
            size_hint=(0.2, 0.1)
        )
        
        self.score_label = Label(
            text=f'Score: {{self.score}}',
            pos_hint={{'x': 0.05, 'y': 0.8}},
            size_hint=(0.2, 0.1)
        )
        
        # Control buttons
        self.fire_button = Button(
            text='FIRE',
            pos_hint={{'x': 0.8, 'y': 0.1}},
            size_hint=(0.15, 0.15),
            background_color=(1, 0, 0, 1)
        )
        self.fire_button.bind(on_press=self.fire_weapon)
        
        layout.add_widget(self.health_label)
        layout.add_widget(self.score_label)
        layout.add_widget(self.fire_button)
        
        self.add_widget(layout)
    
    def update(self, dt):
        """Update game logic."""
        # Update enemies
        for enemy in self.enemies[:]:
            enemy['x'] += enemy['vx'] * dt
            enemy['y'] += enemy['vy'] * dt
            
            # Remove enemies that are off screen
            if (enemy['x'] < 0 or enemy['x'] > Window.width or
                enemy['y'] < 0 or enemy['y'] > Window.height):
                self.enemies.remove(enemy)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['vx'] * dt
            bullet['y'] += bullet['vy'] * dt
            
            # Remove bullets that are off screen
            if (bullet['x'] < 0 or bullet['x'] > Window.width or
                bullet['y'] < 0 or bullet['y'] > Window.height):
                self.bullets.remove(bullet)
        
        # Spawn enemies
        if random.random() < 0.01:
            self.spawn_enemy()
        
        # Update UI
        self.update_ui()
    
    def spawn_enemy(self):
        """Spawn a new enemy."""
        if len(self.enemies) < 5:
            enemy = {{
                'x': random.randint(0, Window.width),
                'y': random.randint(0, Window.height),
                'vx': random.uniform(-100, 100),
                'vy': random.uniform(-100, 100),
                'health': 100
            }}
            self.enemies.append(enemy)
    
    def fire_weapon(self, instance):
        """Fire weapon."""
        # Create bullet
        bullet = {{
            'x': Window.width / 2,
            'y': Window.height / 2,
            'vx': random.uniform(-200, 200),
            'vy': random.uniform(-200, 200)
        }}
        self.bullets.append(bullet)
    
    def update_ui(self):
        """Update UI elements."""
        self.health_label.text = f'Health: {{self.health}}'
        self.score_label.text = f'Score: {{self.score}}'

class MenuScreen(Screen):
    """Main menu screen."""
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = BoxLayout(orientation='vertical', padding=50, spacing=20)
        
        title = Label(
            text='{game_name}',
            font_size='48sp',
            size_hint_y=None,
            height=100
        )
        
        start_button = Button(
            text='Start Game',
            size_hint_y=None,
            height=80,
            background_color=(0, 1, 0, 1)
        )
        start_button.bind(on_press=self.start_game)
        
        layout.add_widget(title)
        layout.add_widget(start_button)
        
        self.add_widget(layout)
    
    def start_game(self, instance):
        """Start the game."""
        self.manager.current = 'game'

class {game_name.replace(' ', '_')}App(App):
    """Main application class."""
    
    def build(self):
        """Build the application."""
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(GameScreen(name='game'))
        return sm

if __name__ == '__main__':
    {game_name.replace(' ', '_')}App().run()
'''
    
    def _generate_pygame_main(self, game_name: str) -> str:
        """Generate Pygame main file."""
        return f'''#!/usr/bin/env python3
"""
{game_name} - Mobile FPS Game with Pygame
"""

import pygame
import math
import random
import sys

class Game:
    """Main game class."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption('{game_name}')
        self.clock = pygame.time.Clock()
        
        # Game state
        self.score = 0
        self.health = 100
        self.enemies = []
        self.bullets = []
        self.running = True
        
        # Player
        self.player_x = 400
        self.player_y = 300
        
        # Colors
        self.WHITE = (255, 255, 255)
        self.BLACK = (0, 0, 0)
        self.RED = (255, 0, 0)
        self.GREEN = (0, 255, 0)
        self.BLUE = (0, 0, 255)
    
    def run(self):
        """Main game loop."""
        while self.running:
            self.handle_events()
            self.update()
            self.render()
            self.clock.tick(60)
        
        pygame.quit()
        sys.exit()
    
    def handle_events(self):
        """Handle game events."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.fire_weapon()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
    
    def update(self):
        """Update game logic."""
        # Update enemies
        for enemy in self.enemies[:]:
            enemy['x'] += enemy['vx']
            enemy['y'] += enemy['vy']
            
            # Remove enemies that are off screen
            if (enemy['x'] < 0 or enemy['x'] > 800 or
                enemy['y'] < 0 or enemy['y'] > 600):
                self.enemies.remove(enemy)
        
        # Update bullets
        for bullet in self.bullets[:]:
            bullet['x'] += bullet['vx']
            bullet['y'] += bullet['vy']
            
            # Remove bullets that are off screen
            if (bullet['x'] < 0 or bullet['x'] > 800 or
                bullet['y'] < 0 or bullet['y'] > 600):
                self.bullets.remove(bullet)
        
        # Spawn enemies
        if random.random() < 0.01:
            self.spawn_enemy()
        
        # Check collisions
        self.check_collisions()
    
    def spawn_enemy(self):
        """Spawn a new enemy."""
        if len(self.enemies) < 5:
            enemy = {{
                'x': random.randint(0, 800),
                'y': random.randint(0, 600),
                'vx': random.uniform(-2, 2),
                'vy': random.uniform(-2, 2),
                'health': 100
            }}
            self.enemies.append(enemy)
    
    def fire_weapon(self):
        """Fire weapon."""
        # Get mouse position
        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        # Calculate direction
        dx = mouse_x - self.player_x
        dy = mouse_y - self.player_y
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            # Create bullet
            bullet = {{
                'x': self.player_x,
                'y': self.player_y,
                'vx': (dx / distance) * 10,
                'vy': (dy / distance) * 10
            }}
            self.bullets.append(bullet)
    
    def check_collisions(self):
        """Check for collisions."""
        # Bullet vs Enemy collisions
        for bullet in self.bullets[:]:
            for enemy in self.enemies[:]:
                distance = math.sqrt(
                    (bullet['x'] - enemy['x'])**2 + 
                    (bullet['y'] - enemy['y'])**2
                )
                if distance < 20:
                    # Enemy hit
                    enemy['health'] -= 25
                    self.bullets.remove(bullet)
                    
                    if enemy['health'] <= 0:
                        self.enemies.remove(enemy)
                        self.score += 100
                    
                    break
    
    def render(self):
        """Render the game."""
        # Clear screen
        self.screen.fill(self.BLACK)
        
        # Draw player
        pygame.draw.circle(self.screen, self.GREEN, 
                         (int(self.player_x), int(self.player_y)), 20)
        
        # Draw enemies
        for enemy in self.enemies:
            pygame.draw.circle(self.screen, self.RED,
                             (int(enemy['x']), int(enemy['y'])), 15)
        
        # Draw bullets
        for bullet in self.bullets:
            pygame.draw.circle(self.screen, self.WHITE,
                             (int(bullet['x']), int(bullet['y'])), 3)
        
        # Draw HUD
        font = pygame.font.Font(None, 36)
        health_text = font.render(f'Health: {{self.health}}', True, self.WHITE)
        score_text = font.render(f'Score: {{self.score}}', True, self.WHITE)
        
        self.screen.blit(health_text, (10, 10))
        self.screen.blit(score_text, (10, 50))
        
        pygame.display.flip()

def main():
    """Main entry point."""
    game = Game()
    game.run()

if __name__ == '__main__':
    main()
'''
    
    def _generate_generic_main(self, game_name: str) -> str:
        """Generate generic main file."""
        return f'''#!/usr/bin/env python3
"""
{game_name} - Mobile FPS Game
"""

import sys
import time

class Game:
    """Main game class."""
    
    def __init__(self):
        self.running = True
        self.score = 0
        self.health = 100
    
    def run(self):
        """Main game loop."""
        print(f"Starting {{game_name}}...")
        
        while self.running:
            self.update()
            time.sleep(0.016)  # ~60 FPS
        
        print("Game ended.")
    
    def update(self):
        """Update game logic."""
        # Game logic would go here
        pass

def main():
    """Main entry point."""
    game = Game()
    game.run()

if __name__ == '__main__':
    main()
'''
    
    def _create_kivy_files(self, game_name: str, platform: str) -> Dict[str, str]:
        """Create Kivy-specific files."""
        files = {}
        
        # Kivy UI file
        files[f"{game_name}/game.kv"] = '''
#:kivy 2.0.0

<GameScreen>:
    canvas.before:
        Color:
            rgba: 0.1, 0.1, 0.1, 1
        Rectangle:
            pos: self.pos
            size: self.size

<MenuScreen>:
    canvas.before:
        Color:
            rgba: 0.2, 0.2, 0.2, 1
        Rectangle:
            pos: self.pos
            size: self.size
'''
        
        # Buildozer spec for Android
        if platform == 'android':
            files[f"{game_name}/buildozer.spec"] = f'''[app]
title = {game_name}
package.name = {game_name.lower().replace(' ', '')}
package.domain = com.example.{game_name.lower().replace(' ', '')}
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

requirements = python3,kivy,pygame,numpy

orientation = landscape
fullscreen = 1
android.permissions = INTERNET,ACCESS_NETWORK_STATE,VIBRATE
android.api = 21
android.minapi = 21
android.sdk = 30
android.ndk = 21b
android.arch = armeabi-v7a arm64-v8a

[buildozer]
log_level = 2
warn_on_root = 1
'''
        
        return files
    
    def _create_pygame_files(self, game_name: str, platform: str) -> Dict[str, str]:
        """Create Pygame-specific files."""
        files = {}
        
        # Pygame configuration
        files[f"{game_name}/pygame_config.py"] = '''
"""
Pygame configuration for mobile game
"""

# Game settings
GAME_TITLE = "Mobile FPS Game"
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Player settings
PLAYER_SPEED = 5
PLAYER_SIZE = 20

# Enemy settings
ENEMY_SPEED = 2
ENEMY_SIZE = 15
MAX_ENEMIES = 5

# Weapon settings
BULLET_SPEED = 10
BULLET_SIZE = 3
'''
        
        return files
    
    def _generate_game_config(self, game_name: str) -> str:
        """Generate game configuration file."""
        return json.dumps({
            'name': game_name,
            'version': '1.0.0',
            'settings': {
                'screen_width': 800,
                'screen_height': 600,
                'fps': 60,
                'fullscreen': False
            },
            'player': {
                'health': 100,
                'speed': 5,
                'jump_force': 10
            },
            'weapons': {
                'assault_rifle': {
                    'damage': 25,
                    'fire_rate': 10,
                    'ammo': 30
                },
                'pistol': {
                    'damage': 35,
                    'fire_rate': 5,
                    'ammo': 15
                }
            },
            'enemies': {
                'max_count': 10,
                'spawn_rate': 0.01,
                'health': 100
            }
        }, indent=2)
    
    def _generate_requirements(self, framework: str) -> str:
        """Generate requirements file."""
        if framework == 'kivy':
            return '''kivy>=2.0.0
pygame>=2.0.0
numpy>=1.20.0
pillow>=8.0.0
'''
        elif framework == 'pygame':
            return '''pygame>=2.0.0
numpy>=1.20.0
'''
        else:
            return '''# Add your dependencies here
'''
    
    def _get_dependencies(self, framework: str) -> List[str]:
        """Get framework dependencies."""
        if framework == 'kivy':
            return ['kivy', 'pygame', 'numpy', 'pillow']
        elif framework == 'pygame':
            return ['pygame', 'numpy']
        else:
            return []
    
    def _create_build_config(self, game_name: str, framework: str, platform: str) -> Dict[str, Any]:
        """Create build configuration."""
        return {
            'game_name': game_name,
            'framework': framework,
            'platform': platform,
            'build_tool': 'buildozer' if framework == 'kivy' and platform == 'android' else 'custom',
            'permissions': [
                'INTERNET',
                'ACCESS_NETWORK_STATE',
                'VIBRATE',
                'RECORD_AUDIO'
            ],
            'min_sdk': 21,
            'target_sdk': 30
        }
    
    def build_game(self, project_path: str, framework: str, platform: str) -> Dict[str, Any]:
        """Build the mobile game."""
        try:
            if framework == 'kivy' and platform == 'android':
                return self._build_kivy_android(project_path)
            elif framework == 'pygame':
                return self._build_pygame(project_path)
            else:
                return {
                    'success': False,
                    'error': f'Building {framework} for {platform} not implemented'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def _build_kivy_android(self, project_path: str) -> Dict[str, Any]:
        """Build Kivy game for Android."""
        try:
            # Run buildozer
            result = subprocess.run(
                ['buildozer', 'android', 'debug'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=300  # 5 minutes timeout
            )
            
            if result.returncode == 0:
                apk_path = os.path.join(project_path, 'bin', 'app-debug.apk')
                if os.path.exists(apk_path):
                    return {
                        'success': True,
                        'platform': 'android',
                        'framework': 'kivy',
                        'apk_path': apk_path,
                        'output': result.stdout
                    }
                else:
                    return {
                        'success': False,
                        'error': 'APK file not found after build'
                    }
            else:
                return {
                    'success': False,
                    'error': result.stderr
                }
        except subprocess.TimeoutExpired:
            return {
                'success': False,
                'error': 'Build timed out'
            }
        except FileNotFoundError:
            return {
                'success': False,
                'error': 'buildozer not found. Install with: pip install buildozer'
            }
    
    def _build_pygame(self, project_path: str) -> Dict[str, Any]:
        """Build Pygame game."""
        try:
            # For Pygame, we just need to ensure it runs
            result = subprocess.run(
                [sys.executable, 'main.py'],
                cwd=project_path,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            return {
                'success': True,
                'platform': 'desktop',
                'framework': 'pygame',
                'output': result.stdout
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    def create_game_assets(self, game_name: str) -> Dict[str, Any]:
        """Create basic game assets."""
        assets = {
            'textures': {
                'player.png': 'Basic player texture',
                'enemy.png': 'Basic enemy texture',
                'bullet.png': 'Basic bullet texture',
                'background.png': 'Game background'
            },
            'sounds': {
                'shoot.wav': 'Weapon firing sound',
                'explosion.wav': 'Explosion sound',
                'background_music.mp3': 'Background music'
            },
            'maps': {
                'desert_warfare.json': 'Desert warfare map',
                'urban_combat.json': 'Urban combat map'
            }
        }
        
        return {
            'success': True,
            'assets': assets,
            'message': 'Asset templates created. Replace with actual assets.'
        }
    
    def generate_documentation(self, game_name: str, framework: str) -> Dict[str, Any]:
        """Generate game documentation."""
        docs = {
            'README.md': f'''# {game_name}

Mobile FPS game created with {framework} framework.

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Run the game:
```bash
python main.py
```

## Building for Mobile

### Android (Kivy)
```bash
buildozer android debug
```

### iOS (Kivy)
```bash
python ios_build.py
```

## Controls

- **Touch/Mouse**: Aim and shoot
- **WASD/Arrow Keys**: Move
- **Space**: Jump
- **R**: Reload
- **ESC**: Pause

## Features

- First-person shooter gameplay
- Multiple weapons
- Enemy AI
- Score system
- Mobile-optimized controls
''',
            'CONTROLS.md': f'''# Game Controls

## Mobile Controls

### Touch Controls
- **Left Joystick**: Move player
- **Right Joystick**: Aim
- **Fire Button**: Shoot weapon
- **Reload Button**: Reload weapon
- **Jump Button**: Jump

### Gesture Controls
- **Swipe**: Look around
- **Double Tap**: Quick reload
- **Pinch**: Zoom in/out

## Desktop Controls

### Keyboard
- **WASD**: Move
- **Mouse**: Look around
- **Left Click**: Shoot
- **R**: Reload
- **Space**: Jump
- **Shift**: Run
- **Ctrl**: Crouch

### Gamepad
- **Left Stick**: Move
- **Right Stick**: Look
- **Right Trigger**: Shoot
- **Left Trigger**: Aim
- **A**: Jump
- **X**: Reload
''',
            'DEVELOPMENT.md': f'''# Development Guide

## Project Structure

```
{game_name}/
├── main.py              # Main game entry point
├── game_config.json     # Game configuration
├── requirements.txt     # Python dependencies
├── src/                 # Source code
│   ├── core/           # Core game systems
│   ├── gameplay/       # Gameplay mechanics
│   ├── graphics/       # Rendering system
│   ├── audio/          # Audio system
│   └── ui/             # User interface
├── assets/             # Game assets
│   ├── models/         # 3D models
│   ├── textures/       # Textures
│   ├── sounds/         # Audio files
│   └── maps/           # Game maps
└── build/              # Build outputs
```

## Adding New Features

### New Weapons
1. Add weapon class in `src/gameplay/weapons.py`
2. Update weapon factory
3. Add weapon models and textures
4. Update UI for weapon selection

### New Maps
1. Create map file in `assets/maps/`
2. Add map loading logic
3. Create map-specific assets
4. Update game configuration

### New Enemies
1. Add enemy class in `src/ai/`
2. Create enemy models and textures
3. Add AI behavior patterns
4. Update spawn system

## Performance Optimization

### Mobile Optimization
- Use texture atlases
- Implement LOD (Level of Detail)
- Optimize draw calls
- Use object pooling
- Implement culling

### Graphics Optimization
- Use efficient shaders
- Implement frustum culling
- Use occlusion culling
- Optimize mesh complexity
- Use texture compression

## Testing

### Unit Tests
```bash
python -m pytest tests/
```

### Performance Tests
```bash
python performance_test.py
```

### Mobile Testing
- Test on various devices
- Test different screen sizes
- Test touch responsiveness
- Test battery usage
'''
        }
        
        return {
            'success': True,
            'documentation': docs
        }