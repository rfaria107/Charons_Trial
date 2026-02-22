import pytest
import pygame
from game.player import Player
from game.enemy import Minotaur

pygame.init()

class DummyPlayer:
    def __init__(self):
        self.rect = pygame.Rect(100, 100, 32, 32)
        self.health = 10
    def take_damage(self, amount):
        self.health -= amount

@pytest.fixture
def minotaur():
    return Minotaur(100, 100)

@pytest.fixture
def player():
    return DummyPlayer()

def test_minotaur_attack(player, minotaur):
    minotaur.rect.topleft = player.rect.topleft
    minotaur.attack(player)
    assert player.health <= 8  # Minotaur should deal damage
