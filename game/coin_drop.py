import pygame

class CoinDrop(pygame.sprite.Sprite):
    COIN_AMOUNT = 1  # Coins per drop; adjust for balance
    FADE_FRAMES = 20

    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        # Gold circle
        pygame.draw.circle(self.image, (255, 215, 0), (6, 6), 6)
        # Outline
        pygame.draw.circle(self.image, (80, 60, 20), (6, 6), 6, 2)
        # Shine
        pygame.draw.line(self.image, (255, 255, 255), (2, 5), (7, 2), 1)
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False
        self.fade_counter = 0

    def update(self, player):
        if not self.collected:
            if self.rect.colliderect(player.rect):
                self.collected = True
                player.add_coins(self.COIN_AMOUNT)
        elif self.fade_counter < self.FADE_FRAMES:
            alpha = int(255 * (1 - self.fade_counter / self.FADE_FRAMES))
            self.image.set_alpha(alpha)
            self.fade_counter += 1

    def draw(self, screen: pygame.Surface, camera=None) -> None:
        draw_pos = camera.apply(self.rect) if camera else self.rect
        screen.blit(self.image, draw_pos)
