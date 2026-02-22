import math
import pygame
from game.player import Player
from game.wave_manager import WaveManager
from game.enemy import Minotaur, Harpy, Satyr, Hydra, Cerberus

def test_wave_spawns_enemies_outside_screen():
    pygame.init()
    player = Player(400, 300)
    enemies = []
    wm = WaveManager()
    # Force a specific spawn: 12 enemies, all types allowed
    enemy_types = [Minotaur, Harpy, Satyr, Hydra, Cerberus]
    wm.spawn_wave(player, enemies, 12, enemy_types, screen_size=(800,600))
    assert len(enemies) == 12
    px, py = player.rect.centerx, player.rect.centery
    min_dist = (max(800,600)/2) + 40  # They're at least 40px outside screen
    for e in enemies:
        dist = math.hypot(e.rect.centerx - px, e.rect.centery - py)
        assert dist > min_dist
