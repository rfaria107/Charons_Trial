import pygame
import pytest
from game.player import Player
from game.ui import HUD
from unittest.mock import Mock

@pytest.fixture
def player():
    pygame.init()
    return Player(400, 300)

@pytest.fixture
def hud(player):
    return HUD(player, 800)

def test_hud_initialization(hud, player):
    assert hud.player == player
    assert hud.screen_width == 800

def test_hud_draw_runs_without_error():
    pygame.init()
    player = Player(400, 300)
    hud = HUD(player, 800)
    # Use a real Surface for this test
    screen = pygame.Surface((800, 600))
    try:
        hud.draw(screen)
    except Exception as e:
        pytest.fail(f"hud.draw() raised an exception: {e}")

def test_player_level_up(player):
    player.add_experience(100)
    assert player.level == 2
    assert player.experience == 0
    assert player.max_experience == 150

    player.add_experience(160)
    assert player.level == 3
    assert player.experience == 10
    assert player.max_experience == 225
