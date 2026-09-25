# Remove duplicate constructor—keep only one __init__, with upgrade and typed attributes
import pygame
from typing import List, Any

class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        try:
            self.image = pygame.image.load('assets/sprites/player/player_spartan.png').convert_alpha()
        except Exception:
            self.image = pygame.Surface((32, 32))
            self.image.fill('blue')
        self.rect = self.image.get_rect(center=(x, y))

        # Player attributes
        self.health = 20
        self.max_health = 20
        self.experience = 0
        self.level = 1
        self.max_experience = 100
        self.speed = 5
        # Enemy collision damage cooldown
        self.damage_cooldown_frames = 36  # ~0.6s
        self.damage_cooldown_counter = 0

        # Coins system for roguelike enhancements
        self.coins = 0

        # Attack attributes
        self.attack_radius = 90
        self.attack_damage = 2
        self.attack_cooldown = 30
        self._attack_timer = 0
        self.auto_attack_fx = 0       # Visual effect timer for auto attacks

        # Cached surfaces for FX to avoid per-frame Surface creation
        self._aura_surface = pygame.Surface((self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self._aura_surface, (120, 180, 255, 100), (self.attack_radius, self.attack_radius), self.attack_radius)
        # Pre-create generic auto attack surface
        self._aa_surface = pygame.Surface((self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
        pygame.draw.circle(self._aa_surface, (90, 220, 250, 140), (self.attack_radius, self.attack_radius), self.attack_radius)

        # Upgrade attributes
        self.upgrades: List[Any] = []
        self.upgrade_levels = {}      # Dict: upgrade name -> stack/level
        self.upgrade_fx: str = ""    # Placeholder for upgrade visual effect
        self.upgrade_fx_timer = 0     # Visual effect timer for ability attacks
        # Artemis Arrow state
        self.artemis_arrow_cooldown_timer = 0
        self.artemis_arrow_upgrades = 0


    def add_upgrade(self, upgrade):
        """Add an upgrade to the player.

        Upgrades with ``apply_once = True`` are applied immediately and never
        stored in ``self.upgrades``; they will never be called again by
        ``auto_attack``.  All other upgrades are stored and called each time
        the auto-attack fires.
        """
        name = upgrade.__class__.__name__
        if name not in self.upgrade_levels:
            self.upgrade_levels[name] = 1
        else:
            self.upgrade_levels[name] += 1

        if getattr(upgrade, "apply_once", False):
            # One-shot: apply now and discard — do NOT add to self.upgrades
            upgrade.activate(self, [])
        else:
            self.upgrades.append(upgrade)
            # Special handling for ArtemisArrow upgrades
            if name == "ArtemisArrow":
                upgrade.upgrade(self)

    def add_coins(self, amount: int):
        """
        Adds the given amount of coins to the player.
        """
        self.coins += amount

    def add_experience(self, amount: int):
        self.experience += amount
        leveled = False
        while self.experience >= self.max_experience:
            self.level_up()
            leveled = True
        return leveled

    def level_up(self):
        self.experience -= self.max_experience
        self.level += 1
        self.max_experience = int(self.max_experience * 1.5)
        # Heal player by 20 HP up to max health after every level up
        self.health = min(self.health + 20, self.max_health)

    def auto_attack(self, enemies: List[Any]):
        """
        Damages enemies within attack_radius. Triggered by cooldown.
        Activates upgrades after normal attack.
        """
        if self._attack_timer == 0:
            attack_area = pygame.Rect(0, 0, self.attack_radius*2, self.attack_radius*2)
            attack_area.center = self.rect.center
            for enemy in enemies:
                if attack_area.colliderect(enemy.rect):
                    enemy.take_damage(self.attack_damage)
            # Activate upgrades
            for upgrade in self.upgrades:
                upgrade.activate(self, enemies)
            self._attack_timer = self.attack_cooldown
            self.auto_attack_fx = 12  # Show visual effect for 12 frames

    def update(self):
        """Advance all timers. Movement is handled by Game._update_player."""
        if self.artemis_arrow_cooldown_timer > 0:
            self.artemis_arrow_cooldown_timer -= 1
        if self.damage_cooldown_counter > 0:
            self.damage_cooldown_counter -= 1
        if self._attack_timer > 0:
            self._attack_timer -= 1
        if self.auto_attack_fx > 0:
            self.auto_attack_fx -= 1
        if self.upgrade_fx_timer > 0:
            self.upgrade_fx_timer -= 1
        # Poseidon cooldown
        if getattr(self, "poseidon_cooldown_timer", 0) > 0:
            self.poseidon_cooldown_timer -= 1
        # Athena shield cooldown and active duration
        if getattr(self, "athena_cooldown_timer", 0) > 0:
            self.athena_cooldown_timer -= 1
        if getattr(self, "athena_shield_timer", 0) > 0:
            self.athena_shield_timer -= 1
        else:
            self.athena_shield_active = False
        # Dionysus cooldown
        if getattr(self, "dionysus_cooldown_timer", 0) > 0:
            self.dionysus_cooldown_timer -= 1

    def take_damage(self, amount: int):
        # Athena shield: ignore damage while active
        if getattr(self, "athena_shield_active", False):
            return
        if self.damage_cooldown_counter == 0:
            self.health -= amount
            self.health = max(0, self.health)
            self.damage_cooldown_counter = self.damage_cooldown_frames

    def move(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_w]:
            self.rect.y -= self.speed
        if keys[pygame.K_s]:
            self.rect.y += self.speed
        if keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_d]:
            self.rect.x += self.speed

    def draw(self, screen: pygame.Surface, camera=None) -> None:
        """Draw the player and visual effects. Uses camera offset when provided."""
        # Determine screen-space position
        draw_rect = camera.apply(self.rect) if camera else self.rect

        aura_rect = self._aura_surface.get_rect(center=draw_rect.center)
        screen.blit(self._aura_surface, aura_rect)

        # Auto attack visual effect
        if self.auto_attack_fx > 0:
            screen.blit(self._aa_surface, aura_rect)

        # Upgrade effect overlay
        if self.upgrade_fx_timer > 0:
            if self.upgrade_fx == "zeus":
                zeus_surface = pygame.Surface((self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(zeus_surface, (240, 240, 36, 210), (self.attack_radius, self.attack_radius), self.attack_radius)
                pygame.draw.circle(zeus_surface, (255, 255, 255, 140), (self.attack_radius, self.attack_radius), self.attack_radius - 10, 2)
                screen.blit(zeus_surface, aura_rect)
            elif self.upgrade_fx == "artemis":
                artemis_surface = pygame.Surface((self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(artemis_surface, (36, 240, 240, 190), (self.attack_radius, self.attack_radius), self.attack_radius)
                pygame.draw.circle(artemis_surface, (255, 255, 255, 90), (self.attack_radius, self.attack_radius), self.attack_radius - 10, 2)
                screen.blit(artemis_surface, aura_rect)
            elif self.upgrade_fx == "poseidon":
                wave_surface = pygame.Surface((self.attack_radius * 4, self.attack_radius * 4), pygame.SRCALPHA)
                wave_rect = wave_surface.get_rect(center=draw_rect.center)
                pygame.draw.circle(wave_surface, (60, 140, 255, 120), (self.attack_radius * 2, self.attack_radius * 2), self.attack_radius * 2, 6)
                screen.blit(wave_surface, wave_rect)
            elif self.upgrade_fx == "athena":
                shield_surface = pygame.Surface((self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(shield_surface, (220, 220, 255, 140), (self.attack_radius, self.attack_radius), self.attack_radius)
                pygame.draw.circle(shield_surface, (180, 180, 255, 220), (self.attack_radius, self.attack_radius), self.attack_radius, 4)
                screen.blit(shield_surface, aura_rect)
            elif self.upgrade_fx == "hermes":
                speed_surface = pygame.Surface((self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(speed_surface, (255, 230, 80, 150), (self.attack_radius, self.attack_radius), self.attack_radius)
                screen.blit(speed_surface, aura_rect)
            elif self.upgrade_fx == "dionysus":
                vine_surface = pygame.Surface((self.attack_radius * 2, self.attack_radius * 2), pygame.SRCALPHA)
                pygame.draw.circle(vine_surface, (100, 220, 60, 160), (self.attack_radius, self.attack_radius), self.attack_radius)
                screen.blit(vine_surface, aura_rect)

        screen.blit(self.image, draw_rect)

        # Clear upgrade_fx only if timer is zero
        if self.upgrade_fx_timer == 0:
            self.upgrade_fx = ""
