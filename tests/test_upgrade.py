import pytest
import pygame
from game.upgrade import (
    ZeusBolt,
    ArtemisArrow,
    IncreaseMaxHealth,
    IncreaseDamage,
    PoseidonWave,
    AthenaShield,
    HermesBoots,
    DionysusVine,
)
from game.player import Player

pygame.init()


@pytest.fixture
def player():
    return Player(50, 50)


class DummyEnemy:
    def __init__(self, x=50, y=50):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.health = 6
        self.fx_type = ""
        self.fx_timer = 0
        self.poison_ticks_remaining = 0
        self.poison_interval_timer = 0

    def take_damage(self, amount):
        self.health -= amount


@pytest.fixture
def enemies():
    return [DummyEnemy(), DummyEnemy()]


# --- Existing upgrade tests ---

def test_zeus_bolt_activation(player, enemies):
    player.add_upgrade(ZeusBolt())
    player._attack_timer = 0
    player.auto_attack(enemies)
    assert sum(e.health for e in enemies) <= 8


def test_artemis_arrow_activation(player, enemies):
    player.add_upgrade(ArtemisArrow())
    player.add_upgrade(ArtemisArrow())
    player._attack_timer = 0
    player.auto_attack(enemies)
    for e in enemies:
        assert e.health <= 4


# --- IncreaseMaxHealth tests ---

def test_increase_max_health(player):
    old_max = player.max_health
    player.health = 5
    player.add_upgrade(IncreaseMaxHealth())
    assert player.max_health == old_max + 20
    assert player.health <= player.max_health


def test_increase_max_health_applies_only_once(player, enemies):
    """Picking the upgrade once must not keep stacking on every auto-attack."""
    player.add_upgrade(IncreaseMaxHealth())
    expected_max = player.max_health  # set after the one-shot apply
    # Fire auto-attack multiple times — health should not grow further
    for _ in range(5):
        player._attack_timer = 0
        player.auto_attack(enemies)
    assert player.max_health == expected_max


def test_increase_max_health_not_in_upgrade_loop(player):
    """One-shot upgrades must not be stored in player.upgrades."""
    player.add_upgrade(IncreaseMaxHealth())
    assert not any(isinstance(u, IncreaseMaxHealth) for u in player.upgrades)


# --- IncreaseDamage tests ---

def test_increase_damage(player):
    old_dmg = player.attack_damage
    player.add_upgrade(IncreaseDamage())
    assert player.attack_damage == old_dmg + IncreaseDamage.DAMAGE_BONUS


def test_increase_damage_stacks(player):
    old_dmg = player.attack_damage
    player.add_upgrade(IncreaseDamage())
    player.add_upgrade(IncreaseDamage())
    assert player.attack_damage == old_dmg + IncreaseDamage.DAMAGE_BONUS * 2


def test_increase_damage_applies_only_once(player, enemies):
    """Damage bonus must not keep growing on every auto-attack."""
    player.add_upgrade(IncreaseDamage())
    expected_dmg = player.attack_damage
    for _ in range(5):
        player._attack_timer = 0
        player.auto_attack(enemies)
    assert player.attack_damage == expected_dmg


def test_increase_damage_not_in_upgrade_loop(player):
    """One-shot upgrades must not be stored in player.upgrades."""
    player.add_upgrade(IncreaseDamage())
    assert not any(isinstance(u, IncreaseDamage) for u in player.upgrades)


# --- PoseidonWave tests ---

def test_poseidon_wave_damages_nearby_enemies(player):
    near = DummyEnemy(player.rect.centerx + 50, player.rect.centery)
    far = DummyEnemy(player.rect.centerx + 500, player.rect.centery)
    upgrade = PoseidonWave()
    upgrade.activate(player, [near, far])
    assert near.health < 6
    assert far.health == 6
    assert player.poseidon_cooldown_timer == PoseidonWave.COOLDOWN


def test_poseidon_wave_respects_cooldown(player):
    near = DummyEnemy(player.rect.centerx + 50, player.rect.centery)
    upgrade = PoseidonWave()
    upgrade.activate(player, [near])
    first_health = near.health
    upgrade.activate(player, [near])
    assert near.health == first_health


# --- AthenaShield tests ---

def test_athena_shield_grants_invulnerability(player):
    upgrade = AthenaShield()
    upgrade.activate(player, [])
    assert getattr(player, "athena_shield_active", False) is True
    player.take_damage(10)
    assert player.health == player.max_health


def test_athena_shield_respects_cooldown(player):
    upgrade = AthenaShield()
    upgrade.activate(player, [])
    old_timer = player.athena_cooldown_timer
    upgrade.activate(player, [])
    assert player.athena_cooldown_timer == old_timer


# --- HermesBoots tests ---

def test_hermes_boots_increases_speed(player):
    old_speed = player.speed
    player.add_upgrade(HermesBoots())
    assert player.speed == old_speed + HermesBoots.SPEED_BONUS


def test_hermes_boots_speed_cap(player):
    player.speed = HermesBoots.MAX_SPEED
    player.add_upgrade(HermesBoots())
    assert player.speed == HermesBoots.MAX_SPEED


def test_hermes_boots_not_in_upgrade_loop(player):
    """One-shot upgrades must not be stored in player.upgrades."""
    player.add_upgrade(HermesBoots())
    assert not any(isinstance(u, HermesBoots) for u in player.upgrades)


# --- DionysusVine tests ---

def test_dionysus_vine_poisons_enemies(player, enemies):
    upgrade = DionysusVine()
    upgrade.activate(player, enemies)
    for e in enemies:
        assert e.poison_ticks_remaining == DionysusVine.POISON_TICKS
    assert player.dionysus_cooldown_timer == DionysusVine.COOLDOWN


def test_dionysus_vine_respects_cooldown(player, enemies):
    upgrade = DionysusVine()
    upgrade.activate(player, enemies)
    first_ticks = enemies[0].poison_ticks_remaining
    upgrade.activate(player, enemies)
    assert enemies[0].poison_ticks_remaining == first_ticks

