import pytest
import pygame
from game.player import Player
from game.upgrade import ZeusBolt, ArtemisArrow

pygame.init()

@pytest.fixture
def player():
    return Player(100, 100)

class DummyEnemy:
    def __init__(self, x=0, y=0):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.health = 10
        self.dead = False
    def take_damage(self, amount):
        self.health -= amount
        if self.health <= 0:
            self.dead = True
    def update(self, player):
        pass
    def draw(self, screen):
        pass

@pytest.fixture
def enemies():
    return [DummyEnemy(100, 100), DummyEnemy(140, 140)]

def test_player_add_upgrade_and_activate(player, enemies):
    player.add_upgrade(ZeusBolt())
    player.add_upgrade(ArtemisArrow())
    player._attack_timer = 0
    player.auto_attack(enemies)
    # ZeusBolt does 4 damage to random enemy, ArtemisArrow does 2 to all
    zeus_targets = [e for e in enemies if e.health <= 6]
    assert len(zeus_targets) >= 1
    assert all(e.health <= 8 for e in enemies)  # All hit by ArtemisArrow
    assert any(e.dead for e in enemies) is False  # No dead yet

def test_upgrade_stack_and_fx(player, enemies):
    player.add_upgrade(ZeusBolt())
    player.add_upgrade(ZeusBolt())
    player._attack_timer = 0
    player.auto_attack(enemies)
    screen = pygame.Surface((200,200))
    # Simulate drawing for duration of FX timer
    for _ in range(16):
        player.update()
        player.draw(screen)
    # Now FX timer should be 0 and FX cleared
    assert player.upgrade_fx == ''

def test_player_take_damage(player):
    player.take_damage(10)
    assert player.health == 10
    # Advance cooldown timer
    player.damage_cooldown_counter = 0
    player.take_damage(1000)
    assert player.health == 0
