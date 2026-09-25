import pygame
from game.player import Player
from game.xp_drop import XPDrop
from main import Game

def test_levelup_flow(tmp_path, monkeypatch):
    # Headless mode is set by test runner AGENTS.md guidance; ensure pygame initialized
    pygame.init()
    # Create game and player
    game = Game()
    game.player.max_experience = 20
    # Give player some XP so a single drop will trigger level-up
    game.player.experience = 10
    # Spawn an XP drop at player location
    xp = XPDrop(game.player.rect.centerx, game.player.rect.centery)
    game.xp_drops.append(xp)
    # Set game to playing so update processes XP drops
    game.state = "playing"
    # Update collects xp and should set leveled_up -> prepare_upgrade_choices -> state level_up
    old_level = game.player.level
    game.update()
    assert game.state == "level_up"
    # Level should already have incremented once by XP collection
    assert game.player.level == old_level + 1
    # Choose first upgrade and press enter equivalent: simulate event effect
    # Instead of sending a pygame event, directly apply selection logic used in handle_events
    chosen = game.upgrade_choices[game.upgrade_selected]
    # Do NOT call level_up here; verify level doesn't increase twice
    game.player.add_upgrade(chosen)
    # After picking, state should go back to playing (simulate handler)
    game.state = "playing"
    assert game.player.level == old_level + 1
