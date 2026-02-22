import pygame

class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y, health=3, speed=1.5, size=20, color=(180, 70, 70)):
        super().__init__()
        self.image = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(self.image, color, (size, size), size)
        self.rect = self.image.get_rect(center=(x, y))
        self.health = health
        self.speed = speed
        self.dead = False
        self.fx_type = ''
        self.fx_timer = 0

    def update(self, player, xp_drops=None, coin_drops=None):
        """Handle death detection, poison ticks, and drop spawning.

        Movement is handled externally (Game._move_with_slide) so that
        axis-separated obstacle collision can be applied cleanly.
        """
        # Dionysus poison: tick damage every POISON_INTERVAL frames
        if getattr(self, "poison_ticks_remaining", 0) > 0:
            timer = getattr(self, "poison_interval_timer", 0)
            if timer <= 0:
                self.take_damage(1)
                self.poison_ticks_remaining -= 1
                self.poison_interval_timer = 60
            else:
                self.poison_interval_timer -= 1

        if self.health <= 0 and not self.dead:
            self.dead = True
            if xp_drops is not None:
                from game.xp_drop import XPDrop
                xp_drops.append(XPDrop(self.rect.centerx, self.rect.centery))
            if coin_drops is not None:
                import random
                from game.coin_drop import CoinDrop
                chance = getattr(self, 'coin_drop_chance', 0.2)
                if random.random() < chance:
                    coin_drops.append(CoinDrop(self.rect.centerx, self.rect.centery))

    def take_damage(self, amt: int):
        self.health -= amt
        if self.health <= 0:
            pass # Enemy death triggers in update, not here

    def draw(self, screen: pygame.Surface, player=None, camera=None) -> None:
        """Draw the enemy. Uses camera offset when provided."""
        draw_rect = camera.apply(self.rect) if camera else self.rect
        screen.blit(self.image, draw_rect)
        # FX Drawing
        if self.fx_timer > 0:
            if self.fx_type == "zeus":
                fx_surface = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
                pygame.draw.ellipse(fx_surface, (255, 255, 120, 180), fx_surface.get_rect())
                screen.blit(fx_surface, draw_rect)
            elif self.fx_type == "artemis" and player is not None:
                player_screen = camera.apply(player.rect).center if camera else player.rect.center
                pygame.draw.line(screen, (120, 255, 210), player_screen, draw_rect.center, 7)
            elif self.fx_type == "poseidon":
                fx_surface = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
                pygame.draw.ellipse(fx_surface, (60, 140, 255, 160), fx_surface.get_rect())
                screen.blit(fx_surface, draw_rect)
            elif self.fx_type == "dionysus":
                fx_surface = pygame.Surface(draw_rect.size, pygame.SRCALPHA)
                pygame.draw.ellipse(fx_surface, (100, 220, 60, 150), fx_surface.get_rect())
                screen.blit(fx_surface, draw_rect)
            self.fx_timer -= 1
            if self.fx_timer <= 0:
                self.fx_type = ''

class Minotaur(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=12, speed=2, size=24, color=(105, 53, 19))
        self.coin_drop_chance = 0.4 # 40% chance
        try:
            self.image = pygame.image.load('assets/sprites/enemies/minotaur.png').convert_alpha()
        except Exception:
            pass
    def attack(self, player):
        player.take_damage(3)

class Harpy(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=4, speed=3, size=18, color=(200, 200, 100))
        self.coin_drop_chance = 0.6 # 60% chance
        try:
            self.image = pygame.image.load('assets/sprites/enemies/harpy.png').convert_alpha()
        except Exception:
            pass

class Satyr(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=3, speed=2.5, size=16, color=(120, 107, 44))
        self.coin_drop_chance = 0.5 # 50% chance
        try:
            self.image = pygame.image.load('assets/sprites/enemies/Satyr.png').convert_alpha()
        except Exception:
            pass

class Hydra(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=15, speed=1.6, size=24, color=(61, 200, 80))
        self.coin_drop_chance = 0.25 # 25% chance
        try:
            self.image = pygame.image.load('assets/sprites/enemies/hydra.png').convert_alpha()
        except Exception:
            pass

class Cerberus(Enemy):
    def __init__(self, x, y):
        super().__init__(x, y, health=8, speed=2.2, size=22, color=(60, 60, 60))
        self.coin_drop_chance = 0.1 # 10% chance
        try:
            self.image = pygame.image.load('assets/sprites/enemies/cerebrus.png').convert_alpha()
        except Exception:
            pass
