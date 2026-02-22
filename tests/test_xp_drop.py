import pytest
import pygame
from game.player import Player
from game.enemy import Enemy
from game.xp_drop import XPDrop

pygame.init()

@pytest.fixture
def player():
    return Player(50, 50)

@pytest.fixture
def enemy():
    return Enemy(50, 50, health=1)

@pytest.fixture
def drops():
    return []

def test_xp_drop_spawn_on_enemy_death(enemy, drops):
    enemy.health = 0
    enemy.update(Player(50, 50), drops)
    assert len(drops) == 1
    assert isinstance(drops[0], XPDrop)

def test_player_collects_single_xp_drop(player, drops):
    drop = XPDrop(player.rect.centerx, player.rect.centery)
    assert player.experience == 0
    drop.update(player)
    assert drop.collected is True
    assert player.experience == 10


def test_player_collects_multiple_xp_drops(player):
    xp_drops = [XPDrop(50, 50), XPDrop(50, 50), XPDrop(51, 50)]
    for xp in xp_drops:
        xp.update(player)
    collected = sum(xp.collected for xp in xp_drops)
    assert collected == 3
    assert player.experience == 30


def test_xp_drop_removed_after_collection(player):
    xp_drops = [XPDrop(50, 50), XPDrop(60, 50)]
    for xp in xp_drops:
        xp.update(player)
    remaining = [xp for xp in xp_drops if not xp.collected]
    assert len(remaining) == 0


def test_player_levels_up_from_xp_drop(player):
    player.max_experience = 20
    xp_drops = [XPDrop(50, 50), XPDrop(51, 51)]
    for xp in xp_drops:
        xp.update(player)
    # Each drop grants 10, so two drops grants 20 XP
    assert player.level == 2


def test_xp_drop_overlapping(player):
    drop1 = XPDrop(player.rect.centerx, player.rect.centery)
    drop2 = XPDrop(player.rect.centerx, player.rect.centery)
    drop1.update(player)
    drop2.update(player)
    assert drop1.collected and drop2.collected
    assert player.experience == 20


def test_xp_drop_with_low_health(player):
    player.health = 1
    drop = XPDrop(player.rect.centerx, player.rect.centery)
    drop.update(player)
    assert player.experience == 10

