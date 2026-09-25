import pygame

class XPDrop(pygame.sprite.Sprite):
    XP_PER_DROP = 10
    FADE_FRAMES = 10

    def __init__(self, x, y):
        super().__init__()
        # Use SRCALPHA surface to avoid requiring a display mode for convert_alpha()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        self.image.fill((60, 155, 255, 255))  # Small blue square with alpha
        self.rect = self.image.get_rect(center=(x, y))
        self.collected = False
        self.fade_counter = 0

    def update(self, player):
        leveled_up = False
        if not self.collected:
            if self.rect.colliderect(player.rect):
                self.collected = True
                leveled_up = player.add_experience(self.XP_PER_DROP)  # Award xp per drop
        elif self.fade_counter < self.FADE_FRAMES:
            alpha = int(255 * (1 - self.fade_counter / self.FADE_FRAMES))
            self.image.set_alpha(alpha)
            self.fade_counter += 1
        return leveled_up

    def draw(self, screen: pygame.Surface, camera=None) -> None:
        draw_pos = camera.apply(self.rect) if camera else self.rect
        screen.blit(self.image, draw_pos)
