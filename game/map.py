import pygame
import random
import math

class Camera:
    """Tracks the world-space offset so the player is always centred on screen."""

    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.x = 0  # world X of the top-left corner of the viewport
        self.y = 0  # world Y of the top-left corner of the viewport

    def follow(self, player_rect: pygame.Rect) -> None:
        """Centre the camera on the player each frame."""
        self.x = player_rect.centerx - self.width // 2
        self.y = player_rect.centery - self.height // 2

    def apply(self, rect: pygame.Rect) -> pygame.Rect:
        """Return a screen-space rect for the given world-space rect."""
        return rect.move(-self.x, -self.y)

    def apply_point(self, wx: int, wy: int) -> tuple:
        """Convert a world-space point to screen-space."""
        return wx - self.x, wy - self.y

# Map generation settings
TILE_SIZE = 64
CHUNK_SIZE = 8  # Number of tiles per chunk edge

# Greek motif tile definitions
TILE_TYPES = [
    "mosaic", "ruins", "olive_tree", "riverbank", "stone_column", "dirt", "temple_floor"
]

# Shared tile sprites loaded once at module level to avoid per-tile I/O.
# floor sprite used for all passable tiles; wall sprite for all obstacles.
def _load_tile_sprites() -> tuple:
    """Load and scale the floor and wall sprites. Returns (floor, wall)."""
    floor_surf = None
    wall_surf = None
    try:
        floor_surf = pygame.image.load("assets/maps/dirt.png").convert()
        floor_surf = pygame.transform.scale(floor_surf, (TILE_SIZE, TILE_SIZE))
    except Exception:
        pass
    try:
        wall_surf = pygame.image.load("assets/maps/wall.png").convert()
        wall_surf = pygame.transform.scale(wall_surf, (TILE_SIZE, TILE_SIZE))
    except Exception:
        pass
    return floor_surf, wall_surf


# Populated on first use (pygame must be initialised before loading images).
_FLOOR_SPRITE: pygame.Surface | None = None
_WALL_SPRITE: pygame.Surface | None = None
_SPRITES_LOADED: bool = False


def _ensure_sprites_loaded() -> None:
    global _FLOOR_SPRITE, _WALL_SPRITE, _SPRITES_LOADED
    if not _SPRITES_LOADED:
        _FLOOR_SPRITE, _WALL_SPRITE = _load_tile_sprites()
        _SPRITES_LOADED = True


class MapTile:
    # Fallback colours when sprites are unavailable
    _FLOOR_COLOR = (150, 110, 50)
    _WALL_COLOR = (100, 80, 140)

    def __init__(self, tx: int, ty: int, tile_type: str, obstacle: bool = False):
        self.tx = tx
        self.ty = ty
        self.tile_type = tile_type
        self.rect = pygame.Rect(tx * TILE_SIZE, ty * TILE_SIZE, TILE_SIZE, TILE_SIZE)
        self.obstacle = obstacle

    def draw(self, screen: pygame.Surface, camera: "Camera") -> None:
        _ensure_sprites_loaded()
        screen_rect = camera.apply(self.rect)
        if self.obstacle:
            if _WALL_SPRITE:
                screen.blit(_WALL_SPRITE, screen_rect)
            else:
                pygame.draw.rect(screen, self._WALL_COLOR, screen_rect)
        else:
            if _FLOOR_SPRITE:
                screen.blit(_FLOOR_SPRITE, screen_rect)
            else:
                pygame.draw.rect(screen, self._FLOOR_COLOR, screen_rect)

class MapChunk:
    def __init__(self, chunk_x: int, chunk_y: int, seed: int = 0):
        random.seed(hash((chunk_x, chunk_y, seed)))
        self.tiles: list = []
        for i in range(CHUNK_SIZE):
            for j in range(CHUNK_SIZE):
                tx = chunk_x * CHUNK_SIZE + i
                ty = chunk_y * CHUNK_SIZE + j
                tile_type = random.choice(TILE_TYPES)
                # Low obstacle density (~5%) so the map stays open and navigable.
                # Only certain thematic tiles can be solid, and only rarely.
                is_obstacle = (
                    tile_type in ("ruins", "stone_column")
                    and random.random() < 0.08
                )
                self.tiles.append(MapTile(tx, ty, tile_type, obstacle=is_obstacle))


class ProceduralMap:
    def __init__(self, seed: int = 0):
        self.seed = seed
        self.loaded_chunks: dict = {}   # (cx, cy) -> MapChunk
        # Spatial index: (tx, ty) -> MapTile, only for obstacle tiles.
        # Gives O(1) collision checks instead of iterating every tile.
        self._obstacle_index: dict = {}

    def _load_chunk(self, cx: int, cy: int) -> None:
        """Load a single chunk and register its obstacle tiles in the index."""
        chunk = MapChunk(cx, cy, self.seed)
        self.loaded_chunks[(cx, cy)] = chunk
        for tile in chunk.tiles:
            if tile.obstacle:
                self._obstacle_index[(tile.tx, tile.ty)] = tile

    def load_chunks_in_view(self, camera_x: int, camera_y: int,
                             width: int, height: int) -> None:
        """Ensure all chunks covering the current viewport are loaded."""
        min_cx = camera_x // (TILE_SIZE * CHUNK_SIZE) - 1
        max_cx = (camera_x + width) // (TILE_SIZE * CHUNK_SIZE) + 1
        min_cy = camera_y // (TILE_SIZE * CHUNK_SIZE) - 1
        max_cy = (camera_y + height) // (TILE_SIZE * CHUNK_SIZE) + 1
        for cx in range(min_cx, max_cx + 1):
            for cy in range(min_cy, max_cy + 1):
                if (cx, cy) not in self.loaded_chunks:
                    self._load_chunk(cx, cy)

    def get_visible_tiles(self, camera_x: int, camera_y: int,
                           width: int, height: int) -> list:
        """Return all tiles whose world rect overlaps the camera viewport."""
        self.load_chunks_in_view(camera_x, camera_y, width, height)
        view_rect = pygame.Rect(camera_x, camera_y, width, height)
        visible: list = []
        for chunk in self.loaded_chunks.values():
            for tile in chunk.tiles:
                if tile.rect.colliderect(view_rect):
                    visible.append(tile)
        return visible

    def check_collision(self, entity_rect: pygame.Rect) -> list:
        """O(1)-per-tile collision check using the obstacle spatial index.

        Only tiles whose grid cell overlaps the entity bounding box are tested,
        so this scales to an unlimited map with no per-frame cost growth.
        """
        # Compute the range of tile coords the entity could overlap.
        min_tx = entity_rect.left // TILE_SIZE
        max_tx = entity_rect.right // TILE_SIZE
        min_ty = entity_rect.top // TILE_SIZE
        max_ty = entity_rect.bottom // TILE_SIZE

        hits: list = []
        for tx in range(min_tx, max_tx + 1):
            for ty in range(min_ty, max_ty + 1):
                tile = self._obstacle_index.get((tx, ty))
                if tile and tile.rect.colliderect(entity_rect):
                    hits.append(tile)
        return hits

    def draw(self, screen: pygame.Surface, camera: "Camera") -> None:
        visible_tiles = self.get_visible_tiles(
            camera.x, camera.y, camera.width, camera.height
        )
        for tile in visible_tiles:
            tile.draw(screen, camera)
