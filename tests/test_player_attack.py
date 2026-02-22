import pygame
import pytest
from game.player import Player
from game.enemy import Enemy

@pytest.fixture
def player():
    pygame.init()
    return Player(400, 300)

@pytest.fixture
def enemy_close():
    return Enemy(420, 300)  # Inside attack radius

@pytest.fixture
def enemy_far():
    return Enemy(520, 300)  # Truly outside attack radius

def test_enemy_damaged_within_attack_radius(player, enemy_close):
    enemies = [enemy_close]
    # Simulate attack
    player._attack_timer = 0
    player.auto_attack(enemies)
    assert enemy_close.health < 20
    assert not enemy_close.dead
    # Hit until enemy dead
    for _ in range(3):
        player._attack_timer = 0
        player.auto_attack(enemies)
    # Enemy.dead is set on update, not take_damage
    enemy_close.update(player)
    assert enemy_close.dead


def test_enemy_not_damaged_outside_attack_radius(player, enemy_far):
    enemies = [enemy_far]
    player._attack_timer = 0
    player.auto_attack(enemies)
    assert enemy_far.health == 3
    assert not enemy_far.dead


def test_attack_cooldown(player, enemy_close):
    enemies = [enemy_close]
    player._attack_timer = 0
    player.auto_attack(enemies)
    first_hit = enemy_close.health
    # Try another attack immediately (should not hit due to cooldown)
    player.auto_attack(enemies)
    assert enemy_close.health == first_hit
    # Lower cooldown and try again
    player._attack_timer = 0
    player.auto_attack(enemies)
    assert enemy_close.health < first_hit

