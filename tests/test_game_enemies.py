import pygame
from main import Game

def test_enemies_spawn():
    pygame.init()
    game = Game()
    # Force wave spawn by manipulating last_wave_time
    game.state = "playing"
    game.wave_manager.last_wave_time -= 10  # simulate 10 seconds elapsed
    game.update()  # This will cause a wave to spawn
    assert len(game.enemies) > 0, "No enemies spawned after game start and forced interval"
