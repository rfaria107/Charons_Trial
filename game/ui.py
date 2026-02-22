import pygame

class HUD:
    def __init__(self, player, screen_width):
        self.player = player
        self.screen_width = screen_width
        self.health_bar_pos = (10, 10)
        self.xp_bar_pos = (10, 40)
        self.bar_length = 300
        self.bar_height = 20

        # Greek-themed colors
        self.health_color = (204, 0, 0)  # Spartan red
        self.xp_color = (255, 215, 0)     # Golden fleece
        self.bar_bg_color = (50, 50, 50)
        self.border_color = (218, 165, 32) # Gold border

    def draw(self, screen):
        self._draw_health_bar(screen)
        self._draw_xp_bar(screen)
        self._draw_level(screen)
        self._draw_coins(screen)

    def _draw_bar(self, screen, pos, length, height, fill_ratio, bar_color, bg_color, border_color):
        # Background
        bg_rect = pygame.Rect(pos[0], pos[1], length, height)
        pygame.draw.rect(screen, bg_color, bg_rect)

        # Fill
        fill_length = length * fill_ratio
        fill_rect = pygame.Rect(pos[0], pos[1], fill_length, height)
        pygame.draw.rect(screen, bar_color, fill_rect)

        # Border
        pygame.draw.rect(screen, border_color, bg_rect, 2)
        # Pillar decorations
        for x in [pos[0], pos[0] + length - 4]:
            pygame.draw.rect(screen, border_color, (x-4, pos[1]-4, 8, height+8),2)
            pygame.draw.rect(screen, self.bar_bg_color, (x-2, pos[1]-2, 4, height+4))
            pygame.draw.line(screen, border_color, (x, pos[1]), (x,pos[1]+height), 2)


    def _draw_health_bar(self, screen):
        health_ratio = self.player.health / self.player.max_health
        self._draw_bar(screen, self.health_bar_pos, self.bar_length, self.bar_height, health_ratio, self.health_color, self.bar_bg_color, self.border_color)
        # Health text
        font = pygame.font.SysFont("Arial", 18)
        text = font.render(f'Health: {self.player.health}/{self.player.max_health}', True, (255,255,255))
        screen.blit(text, (self.health_bar_pos[0] + 5, self.health_bar_pos[1] + 2))

    def _draw_xp_bar(self, screen):
        xp_ratio = self.player.experience / self.player.max_experience
        self._draw_bar(screen, self.xp_bar_pos, self.bar_length, self.bar_height, xp_ratio, self.xp_color, self.bar_bg_color, self.border_color)
        # XP text
        font = pygame.font.SysFont("Arial", 18)
        text = font.render(f'XP: {self.player.experience}/{self.player.max_experience}', True, (0,0,0))
        screen.blit(text, (self.xp_bar_pos[0] + 5, self.xp_bar_pos[1] + 2))


    def _draw_level(self, screen):
        font = pygame.font.SysFont("Perpetua", 32, bold=True)
        text = font.render(f'Lvl: {self.player.level}', True, self.border_color)
        text_rect = text.get_rect(midleft=(self.health_bar_pos[0] + self.bar_length + 20, self.health_bar_pos[1] + self.bar_height))
        screen.blit(text, text_rect)

    def _draw_coins(self, screen):
        # Draw gold coin icon
        coin_pos = (10, 70)
        pygame.draw.circle(screen, (255, 215, 0), (coin_pos[0] + 12, coin_pos[1] + 12), 12)
        # Draw coin count
        font = pygame.font.SysFont("Arial", 20, bold=True)
        coins_text = font.render(f'Coins: {self.player.coins}', True, (218, 165, 32))
        screen.blit(coins_text, (coin_pos[0] + 30, coin_pos[1] + 5))
