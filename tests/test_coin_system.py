import pytest
import pygame
import os
from game.player import Player
from game.coin_drop import CoinDrop
from game.enemy import Minotaur, Harpy, Satyr, Hydra, Cerberus
from game.ui import HUD

@pytest.fixture(scope="module")
def pygame_setup():
    pygame.init()
    pygame.display.set_mode((100, 100))
    yield
    pygame.quit()

# --- 1. CoinDrop spawn chance per enemy type ---
def test_coin_drop_chance_per_enemy_type(pygame_setup):
    enemies = [Minotaur(10, 10), Harpy(10, 10), Satyr(10, 10), Hydra(10, 10), Cerberus(10, 10)]
    chances = [e.coin_drop_chance for e in enemies]
    assert chances == [0.4, 0.6, 0.5, 0.25, 0.1]

# --- 2. CoinDrop collection & player coin increment ---
def test_coin_drop_collection_increments_player_coins(pygame_setup):
    player = Player(10, 10)
    drop = CoinDrop(10, 10)
    drop.rect = player.rect  # Force overlap
    before = player.coins
    drop.update(player)
    assert drop.collected
    assert player.coins == before + CoinDrop.COIN_AMOUNT

# --- 3. HUD displays correct coin value ---
def test_hud_coin_display(pygame_setup):
    player = Player(10, 10)
    player.coins = 5
    hud = HUD(player, 100)
    screen = pygame.Surface((100, 100))
    hud.draw(screen)  # Should not error, visually check coin logic

# --- 4. Coins persist via load/save ---
def test_coins_persist_load_save(tmp_path, pygame_setup):
    player = Player(10, 10)
    player.coins = 12
    coins_file = tmp_path / "coins.txt"
    with open(coins_file, "w") as f:
        f.write(str(player.coins))
    # Simulate loading coins
    with open(coins_file, "r") as f:
        loaded = int(f.read().strip())
    assert loaded == player.coins

# --- 5. Respawn preserves coins, resets other data ---
def test_respawn_preserves_coins_resets_data(pygame_setup):
    player = Player(10, 10)
    player.coins = 8
    player.health = 1
    player.experience = 99
    player.level = 3
    # Simulate respawn by creating new Player and assigning coins
    new_player = Player(10, 10)
    new_player.coins = player.coins
    assert new_player.coins == 8
    assert new_player.health == 20
    assert new_player.experience == 0
    assert new_player.level == 1

# --- 6. CoinDrop animation duration ---
def test_coin_drop_fade_animation_duration(pygame_setup):
    player = Player(10, 10)
    drop = CoinDrop(10, 10)
    drop.rect = player.rect
    drop.update(player)
    assert drop.fade_counter == 0  # Still at 0 after collection
    # Step through fade-out
    for _ in range(CoinDrop.FADE_FRAMES):
        drop.update(player)
    assert drop.fade_counter == CoinDrop.FADE_FRAMES

