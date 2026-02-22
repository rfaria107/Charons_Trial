from typing import Protocol, List, Any
import pygame
import random
import math


class Upgrade(Protocol):
    def activate(self, player: Any, enemies: List[Any]) -> None:
        ...

    def deactivate(self, player: Any) -> None:
        ...


class ZeusBolt:
    """Strikes a random enemy with a lightning bolt dealing 4 damage."""

    def activate(self, player: Any, enemies: List[Any]) -> None:
        if enemies:
            target = random.choice(enemies)
            target.take_damage(4)
            target.fx_type = "zeus"
            target.fx_timer = 16

    def deactivate(self, player: Any) -> None:
        pass


class ArtemisArrow:
    """Fires a moonlit arrow at one (or more) enemies on a cooldown."""

    def __init__(self) -> None:
        self.base_damage = 2
        self.damage = 2
        self.max_targets = 1
        self.cooldown = 90  # 1.5 s at 60 fps

    def activate(self, player: Any, enemies: List[Any]) -> None:
        if getattr(player, "artemis_arrow_cooldown_timer", 0) == 0:
            targets = random.sample(enemies, min(self.max_targets, len(enemies)))
            for enemy in targets:
                enemy.take_damage(self.damage)
                enemy.fx_type = "artemis"
                enemy.fx_timer = 16
            player.artemis_arrow_cooldown_timer = self.cooldown

    def deactivate(self, player: Any) -> None:
        pass

    def upgrade(self, player: Any) -> None:
        """Alternate between +1 target and +1 damage per stack."""
        upgrades = getattr(player, "artemis_arrow_upgrades", 0)
        if upgrades % 2 == 0:
            self.max_targets += 1
        else:
            self.damage += 1
        player.artemis_arrow_upgrades = upgrades + 1


class IncreaseMaxHealth:
    """Permanently raises max health by 20 and heals the same amount.

    Applied once at pick time; never stored in the auto-attack upgrade list.
    """

    apply_once: bool = True
    HEALTH_BONUS = 20

    def activate(self, player: Any, enemies: List[Any]) -> None:
        player.max_health += self.HEALTH_BONUS
        player.health = min(player.health + self.HEALTH_BONUS, player.max_health)

    def deactivate(self, player: Any) -> None:
        pass


class IncreaseDamage:
    """Permanently raises the player's base auto-attack damage by 1.

    Applied once at pick time; never stored in the auto-attack upgrade list.
    Each stack grants another +1.
    """

    apply_once: bool = True
    DAMAGE_BONUS = 1

    def activate(self, player: Any, enemies: List[Any]) -> None:
        player.attack_damage += self.DAMAGE_BONUS

    def deactivate(self, player: Any) -> None:
        pass


class PoseidonWave:
    """Unleashes a tidal wave that pushes all nearby enemies away from the
    player and deals 2 damage to each. Fires on a 4-second cooldown."""

    COOLDOWN = 240  # 4 s at 60 fps
    RADIUS = 200
    KNOCKBACK = 48
    DAMAGE = 2

    def activate(self, player: Any, enemies: List[Any]) -> None:
        timer_attr = "poseidon_cooldown_timer"
        if getattr(player, timer_attr, 0) == 0:
            px, py = player.rect.centerx, player.rect.centery
            for enemy in enemies:
                ex, ey = enemy.rect.centerx, enemy.rect.centery
                dist = math.hypot(ex - px, ey - py)
                if dist <= self.RADIUS and dist > 0:
                    # Push enemy directly away from player
                    nx = (ex - px) / dist
                    ny = (ey - py) / dist
                    enemy.rect.x += int(nx * self.KNOCKBACK)
                    enemy.rect.y += int(ny * self.KNOCKBACK)
                    enemy.take_damage(self.DAMAGE)
                    enemy.fx_type = "poseidon"
                    enemy.fx_timer = 20
            setattr(player, timer_attr, self.COOLDOWN)
            # Signal the player draw to show a wave ring
            player.upgrade_fx = "poseidon"
            player.upgrade_fx_timer = 20

    def deactivate(self, player: Any) -> None:
        pass


class AthenaShield:
    """Grants a brief window of invulnerability (60 frames / 1 s) on a
    5-second cooldown. Stacking reduces the cooldown by 30 frames each time."""

    BASE_COOLDOWN = 300  # 5 s
    COOLDOWN_REDUCTION = 30
    SHIELD_DURATION = 60  # 1 s

    def __init__(self) -> None:
        self.cooldown = self.BASE_COOLDOWN

    def activate(self, player: Any, enemies: List[Any]) -> None:
        timer_attr = "athena_cooldown_timer"
        active_attr = "athena_shield_active"
        duration_attr = "athena_shield_timer"
        if getattr(player, timer_attr, 0) == 0:
            setattr(player, active_attr, True)
            setattr(player, duration_attr, self.SHIELD_DURATION)
            setattr(player, timer_attr, self.cooldown)
            player.upgrade_fx = "athena"
            player.upgrade_fx_timer = self.SHIELD_DURATION

    def deactivate(self, player: Any) -> None:
        pass

    def upgrade(self, player: Any) -> None:
        """Each additional stack shortens the cooldown."""
        self.cooldown = max(60, self.cooldown - self.COOLDOWN_REDUCTION)


class HermesBoots:
    """A one-time blessing that permanently raises the player's move speed.
    Each stack adds +1 to speed (up to a reasonable cap).

    Applied once at pick time; never stored in the auto-attack upgrade list.
    """

    apply_once: bool = True
    SPEED_BONUS = 1
    MAX_SPEED = 12

    def activate(self, player: Any, enemies: List[Any]) -> None:
        if player.speed < self.MAX_SPEED:
            player.speed += self.SPEED_BONUS
        # Briefly show a speed-up FX
        player.upgrade_fx = "hermes"
        player.upgrade_fx_timer = 30

    def deactivate(self, player: Any) -> None:
        pass


class DionysusVine:
    """Poisons all enemies currently on screen, dealing 1 damage per second
    for 3 seconds (ticked every 60 frames). Fires on a 6-second cooldown."""

    COOLDOWN = 360  # 6 s
    POISON_TICKS = 3
    POISON_INTERVAL = 60  # 1 tick per second
    POISON_DAMAGE = 1

    def activate(self, player: Any, enemies: List[Any]) -> None:
        timer_attr = "dionysus_cooldown_timer"
        if getattr(player, timer_attr, 0) == 0:
            for enemy in enemies:
                # Add poison state directly onto each enemy object
                poison_ticks = getattr(enemy, "poison_ticks_remaining", 0)
                enemy.poison_ticks_remaining = poison_ticks + self.POISON_TICKS
                enemy.poison_interval_timer = self.POISON_INTERVAL
                enemy.fx_type = "dionysus"
                enemy.fx_timer = 30
            setattr(player, timer_attr, self.COOLDOWN)
            player.upgrade_fx = "dionysus"
            player.upgrade_fx_timer = 30

    def deactivate(self, player: Any) -> None:
        pass
