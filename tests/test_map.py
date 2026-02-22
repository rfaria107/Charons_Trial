import pytest
import pygame
from game.map import ProceduralMap, Camera, MapTile

pygame.init()

def test_procedural_map_chunks_load():
    screen_w, screen_h = 400, 300
    camera = Camera(screen_w, screen_h)
    player_rect = pygame.Rect(200, 150, 32, 32)
    camera.follow(player_rect)
    procedural_map = ProceduralMap(seed=4)
    procedural_map.load_chunks_in_view(camera.x, camera.y, screen_w, screen_h)
    assert len(procedural_map.loaded_chunks) > 0


def test_procedural_map_collision_detection():
    procedural_map = ProceduralMap(seed=7)
    # Place camera so chunk loads
    procedural_map.load_chunks_in_view(0, 0, 400, 300)
    # Find an obstacle tile
    obstacles = [tile for chunk in procedural_map.loaded_chunks.values() 
                 for tile in chunk.tiles if tile.obstacle]
    if obstacles:
        # Entity overlaps obstacle
        test_rect = pygame.Rect(obstacles[0].rect)
        collisions = procedural_map.check_collision(test_rect)
        assert len(collisions) > 0
    else:
        pytest.skip("No obstacles spawned in chunk; rerun test")


def test_procedural_map_draw_sprite_or_color():
    screen = pygame.Surface((128, 128))
    camera = Camera(128, 128)
    procedural_map = ProceduralMap()
    procedural_map.load_chunks_in_view(0, 0, 128, 128)
    tiles = procedural_map.get_visible_tiles(0, 0, 128, 128)
    for tile in tiles[:5]:
        tile.draw(screen, camera)  # Should not error, regardless of sprite/color
    assert True  # Drawing completed successfully
