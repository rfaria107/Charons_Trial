import os
import pygame

# Game core loop and orchestration
from game.player import Player
from game.ui import HUD
from game.enemy import Minotaur, Hydra, Cerberus

class Game:
    def __init__(self):
        pygame.init()
        # Use pygame.font for text rendering (pygame.freetype not required)
        pygame.font.init()
        self.screen = pygame.display.set_mode((800, 600))
        pygame.display.set_caption("Charon's Trial")
        self.clock = pygame.time.Clock()
        self.running = True
        self.player = Player(400, 300)
        self.hud = HUD(self.player, self.screen.get_width())
        self.enemies = []
        self.xp_drops = []
        self.coin_drops = []
        from game.wave_manager import WaveManager
        self.wave_manager = WaveManager()
        # Map & camera integration
        from game.map import Camera, ProceduralMap
        self.camera = Camera(self.screen.get_width(), self.screen.get_height())
        self.procedural_map = ProceduralMap(seed=42)
        self.state = "menu"
        self.menu_options = ["Start Game", "Quit"]
        self.menu_selected = 0
        self.upgrade_choices = []
        self.upgrade_selected = 0
        self.load_coins()


    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                # Main menu/game state transitions
                if self.state == "menu":
                    if event.key == pygame.K_UP:
                        self.menu_selected = (self.menu_selected - 1) % len(self.menu_options)
                    elif event.key == pygame.K_DOWN:
                        self.menu_selected = (self.menu_selected + 1) % len(self.menu_options)
                    elif event.key == pygame.K_RETURN:
                        if self.menu_selected == 0:
                            self.state = "playing"
                        elif self.menu_selected == 1:
                            self.running = False
                elif self.state == "playing":
                    if event.key == pygame.K_ESCAPE:
                        self.state = "paused"
                elif self.state == "paused":
                    if event.key in (pygame.K_ESCAPE, pygame.K_p):
                        self.state = "playing"
                elif self.state == "game_over":
                    if event.key == pygame.K_RETURN:
                        self.reset_game()
                        self.state = "playing"
                elif self.state == "level_up":
                    # Upgrade picker: arrow keys to move, Enter to choose
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        self.upgrade_selected = min(self.upgrade_selected + 1, len(self.upgrade_choices) - 1)
                    elif event.key in (pygame.K_LEFT, pygame.K_a):
                        self.upgrade_selected = max(self.upgrade_selected - 1, 0)
                    elif event.key == pygame.K_RETURN:
                        chosen = self.upgrade_choices[self.upgrade_selected]
                        self.player.level_up()  # Increment level/stats
                        self.player.add_upgrade(chosen)
                        self.state = "playing"

    def update(self):
        if self.state == "playing":
            self._update_player()
            self.player.auto_attack(self.enemies)
            self._update_enemies()

            # Remove dead enemies
            self.enemies = [e for e in self.enemies if not e.dead]

            # XP DROP: update and collect
            leveled_up = False
            for xp in self.xp_drops:
                if xp.update(self.player):
                    leveled_up = True
            self.xp_drops = [xp for xp in self.xp_drops if not (xp.collected and xp.fade_counter >= xp.FADE_FRAMES)]
            if leveled_up and self.state == "playing":
                self.prepare_upgrade_choices()
                self.state = "level_up"

            # COIN DROP: update and collect
            for coin in self.coin_drops:
                coin.update(self.player)
            self.coin_drops = [coin for coin in self.coin_drops if not (coin.collected and coin.fade_counter >= coin.FADE_FRAMES)]

            # Spawn waves
            self.wave_manager.update(self.player, self.enemies)

            # Game over check
            if self.player.health <= 0:
                self.state = "game_over"

    def _move_with_slide(self, rect: pygame.Rect, dx: int, dy: int) -> None:
        """Move rect by (dx, dy) with axis-separated obstacle sliding.

        Each axis is applied independently so the entity slides along walls
        instead of being frozen in place on any diagonal contact.
        """
        # --- X axis ---
        rect.x += dx
        if self.procedural_map.check_collision(rect):
            rect.x -= dx  # revert only X

        # --- Y axis ---
        rect.y += dy
        if self.procedural_map.check_collision(rect):
            rect.y -= dy  # revert only Y

    def _update_player(self) -> None:
        """Advance player timers then apply movement with obstacle sliding."""
        self.player.update()  # advances all cooldown timers

        # Compute intended displacement from keys and slide against obstacles
        keys = pygame.key.get_pressed()
        dx = (keys[pygame.K_d] - keys[pygame.K_a]) * self.player.speed
        dy = (keys[pygame.K_s] - keys[pygame.K_w]) * self.player.speed
        self._move_with_slide(self.player.rect, dx, dy)

    def _update_enemies(self) -> None:
        """Update all enemies with obstacle-sliding movement and contact damage."""
        import math
        for enemy in self.enemies:
            # Compute pursuit direction
            edx = self.player.rect.centerx - enemy.rect.centerx
            edy = self.player.rect.centery - enemy.rect.centery
            dist = max(math.hypot(edx, edy), 1)
            dx = int(enemy.speed * edx / dist)
            dy = int(enemy.speed * edy / dist)

            # Move with axis-separated sliding
            self._move_with_slide(enemy.rect, dx, dy)

            # Handle death / drops (call update without moving again)
            enemy.update(self.player, self.xp_drops, self.coin_drops)

            # Contact damage to player
            if enemy.rect.colliderect(self.player.rect):
                if self.player.damage_cooldown_counter == 0:
                    if isinstance(enemy, Minotaur):
                        self.player.take_damage(3)
                    elif isinstance(enemy, Hydra):
                        self.player.take_damage(3)
                    elif isinstance(enemy, Cerberus):
                        self.player.take_damage(2)
                    else:
                        self.player.take_damage(1)

    def draw(self):
        # Update camera to centre on player every frame
        self.camera.follow(self.player.rect)

        if self.state == "menu":
            self.screen.fill((40, 34, 20))
            # Greek-styled overlay for main menu
            overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
            overlay.fill((40, 34, 20, 210))  # gold-brown translucent
            self.screen.blit(overlay, (0, 0))
            # Pillar accents left/right (columns)
            pillar_color = (218, 165, 32)
            pygame.draw.rect(self.screen, pillar_color, (40, 40, 32, 520), 0, border_radius=10)
            pygame.draw.rect(self.screen, pillar_color, (728, 40, 32, 520), 0, border_radius=10)
            # Title
            title_font = pygame.font.SysFont("Times New Roman", 48, bold=True)
            title = title_font.render("CHARON'S TRIAL", True, (220, 210, 120))
            # Title
            screen_width = self.screen.get_width()
            title_rect = title.get_rect(center=(screen_width // 2, 100))
            self.screen.blit(title, title_rect.topleft)
            # Menu options (centered, spaced, Greek font, gold border)
            menu_font = pygame.font.SysFont("Perpetua", 38)
            pillar_margin_left = 72
            pillar_margin_right = 728
            content_width = pillar_margin_right - pillar_margin_left
            num_options = len(self.menu_options)
            box_w, box_h = 260, 55
            box_spacing = 30
            start_y = 240
            for idx, option in enumerate(self.menu_options):
                x = pillar_margin_left + (content_width - box_w) // 2
                y = start_y + idx * (box_h + box_spacing)
                box_color = (180, 160, 80, 180) if idx == self.menu_selected else (90, 70, 40, 180)
                box_surface = pygame.Surface((box_w, box_h), pygame.SRCALPHA)
                box_surface.fill(box_color)
                self.screen.blit(box_surface, (x, y))
                pygame.draw.rect(self.screen, pillar_color, (x, y, box_w, box_h), 3, border_radius=8)
                option_text = menu_font.render(option, True, (250, 240, 160))
                text_rect = option_text.get_rect(center=(x + box_w // 2, y + box_h // 2))
                self.screen.blit(option_text, text_rect.topleft)
            # Instructions
            instr_font = pygame.font.SysFont("Arial", 22)
            instructions = instr_font.render("Up/Down: Move | Enter: Select", True, (255, 220, 170))
            self.screen.blit(instructions, (245, 390))
            # Riverbank accent
            pygame.draw.rect(self.screen, (80, 80, 120), (0, 570, 800, 30))
            pygame.display.flip()
            return

        # Draw procedural map as background (world-space tiles offset by camera)
        self.procedural_map.draw(self.screen, self.camera)

        # Draw XP drops
        for xp in self.xp_drops:
            xp.draw(self.screen, self.camera)
        # Draw Coin drops
        for coin in self.coin_drops:
            coin.draw(self.screen, self.camera)
        # Draw player and enemies at camera-offset positions
        self.player.draw(self.screen, self.camera)
        for enemy in self.enemies:
            enemy.draw(self.screen, self.player, self.camera)
        self.hud.draw(self.screen)
        # Add UI drawing here (score, health, etc.)
        if self.state == "paused":
            self._draw_overlay("PAUSED", (200, 200, 200))
        elif self.state == "game_over":
            self._draw_overlay("GAME OVER\nPress Enter to Restart", (220, 60, 60))
        elif self.state == "level_up":
            self.draw_upgrade_picker()
        pygame.display.flip()

    def draw_upgrade_picker(self):
        # Greek-styled overlay
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((40, 34, 20, 180))  # gold-brown translucent
        self.screen.blit(overlay, (0, 0))
        font = pygame.font.SysFont("Times New Roman", 40, bold=True)
        small_font = pygame.font.SysFont("Arial", 22)
        upgrade_font = pygame.font.SysFont("Perpetua", 32)
        # Title (centered)
        screen_width = self.screen.get_width()
        title = font.render("CHOOSE YOUR BLESSING", True, (220, 210, 120))
        title_rect = title.get_rect(center=(screen_width // 2, 100))
        self.screen.blit(title, title_rect.topleft)
        # Center upgrade boxes as a group
        box_w, box_h = 230, 110
        spacing = 30
        num_options = len(self.upgrade_choices)
        total_group_width = num_options * box_w + (num_options - 1) * spacing
        start_x = (screen_width - total_group_width) // 2
        y = 200
        for idx, upgrade in enumerate(self.upgrade_choices):
            name = upgrade.__class__.__name__
            level = self.player.upgrade_levels.get(name, 0)
            x = start_x + idx * (box_w + spacing)
            # Highlight
            box_color = (180, 160, 80) if idx == self.upgrade_selected else (100, 70, 40)
            pygame.draw.rect(self.screen, box_color, (x, y, box_w, box_h), 0, border_radius=16)
            pygame.draw.rect(self.screen, (220, 210, 120), (x, y, box_w, box_h), 3, border_radius=16)
            # Name
            utext = upgrade_font.render(name, True, (255,255,210))
            utext_rect = utext.get_rect(center=(x + box_w // 2, y + 30))
            self.screen.blit(utext, utext_rect.topleft)
            # Level badge
            lvl_text = small_font.render(f"Level: {level}", True, (235,215,40))
            pygame.draw.circle(self.screen, (255,215,40), (x + box_w // 2, y + 75), 22)
            self.screen.blit(lvl_text, (x + box_w // 2 - 25, y + 65))
            # If highlighted, draw effect
            if idx == self.upgrade_selected:
                pygame.draw.rect(self.screen, (255,225,110), (x-2, y-2, box_w+4, box_h+4), 2, border_radius=18)
        # Instructions (centered)
        help_text = small_font.render("Left/Right: Move | Enter: Select", True, (255,220,170))
        help_rect = help_text.get_rect(center=(screen_width // 2, 340))
        self.screen.blit(help_text, help_rect.topleft)


    def run(self):
        while self.running:
            self.handle_events()
            if self.state == "upgrade":
                # Draw upgrade menu (stub; could merge with level_up for now)
                self.draw()
            elif self.state == "level_up":
                # Draw level up screen
                self.draw()
            else:
                if self.state == "game_over" or self.state == "paused":
                    self.draw()
                else:
                    self.update()
                    self.draw()
            self.clock.tick(60)
        self.save_coins()
        pygame.quit()

    def load_coins(self):
        try:
            with open('coins.txt', 'r') as f:
                coins = int(f.read().strip())
                self.player.coins = coins
        except Exception:
            self.player.coins = 0

    def save_coins(self):
        try:
            with open('coins.txt', 'w') as f:
                f.write(str(self.player.coins))
        except Exception:
            pass

    def _draw_overlay(self, text, color=(255,255,255)):
        # Overlay box and centered text for pause/game over/level up
        overlay = pygame.Surface(self.screen.get_size(), pygame.SRCALPHA)
        overlay.fill((0,0,0, 160))  # semi-translucent background
        self.screen.blit(overlay, (0,0))
        font = pygame.font.SysFont("Arial", 54)
        lines = text.split("\n")
        for i, line in enumerate(lines):
            rendered = font.render(line, True, color)
            rect = rendered.get_rect(center=(400, 260 + i*70))
            self.screen.blit(rendered, rect)

    def prepare_upgrade_choices(self):
        # Pick 3 unique upgrades from the full Greek-themed pool
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
        import random

        pool = [
            ZeusBolt(),
            ArtemisArrow(),
            IncreaseMaxHealth(),
            IncreaseDamage(),
            PoseidonWave(),
            AthenaShield(),
            HermesBoots(),
            DionysusVine(),
        ]
        self.upgrade_choices = random.sample(pool, k=min(3, len(pool)))
        self.upgrade_selected = 0

    def reset_game(self):
        # Robust reset: reinitialize player, enemies, wave manager, xp drops, coin drops
        self.player = Player(400, 300)
        self.hud = HUD(self.player, self.screen.get_width())
        self.enemies = []
        self.xp_drops = []
        self.coin_drops = []
        from game.wave_manager import WaveManager
        self.wave_manager = WaveManager()
        # Reinitialise camera and map so chunk offsets don't persist across runs
        from game.map import Camera, ProceduralMap
        self.camera = Camera(self.screen.get_width(), self.screen.get_height())
        self.procedural_map = ProceduralMap(seed=42)
        self.load_coins()
        # Player constructor resets health, xp, level, upgrades, fx. HUD now points to fresh player state.

if __name__ == '__main__':
    game = Game()
    game.run()
