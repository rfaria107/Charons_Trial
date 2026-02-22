import time
import random
from game.enemy import Minotaur, Harpy, Satyr, Hydra, Cerberus

class WaveManager:
    def __init__(self):
        self.wave = 1
        self.last_wave_time = time.time()
        self.wave_interval = 8.0   # seconds between waves
        self.waves_started = 0

    def update(self, player, enemies):
        now = time.time()
        if now - self.last_wave_time >= self.wave_interval:
            num_enemies = min(5 + self.wave * 2, 40)  # scale up, clamp to 40
            types = [Minotaur, Harpy, Satyr, Hydra, Cerberus]
            self.spawn_wave(player, enemies, num_enemies, types)
            self.wave += 1
            self.last_wave_time = now

    def spawn_wave(self, player, enemies, num_enemies, enemy_types, screen_size=(800,600)):
        px, py = player.rect.centerx, player.rect.centery
        screen_w, screen_h = screen_size
        radius = int(max(screen_w, screen_h) / 2) + 500  # spawn just off visible area by 100px
        for _ in range(num_enemies):
            angle = random.uniform(0, 2 * 3.14159265)
            spawn_x = px + radius * random.uniform(0.95, 1.05) * math.cos(angle)
            spawn_y = py + radius * random.uniform(0.95, 1.05) * math.sin(angle)
            # Pick random enemy type; later could bias by wave
            EnemyClass = random.choice(enemy_types)
            enemies.append(EnemyClass(spawn_x, spawn_y))
        # Could later: check for wall collisions, stack, tile occupied

import math
