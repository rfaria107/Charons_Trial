# Charon's Trial

A Greek-mythology auto-battler roguelike built in Python with Pygame. Fight your way through procedurally generated, infinite maps against waves of mythological enemies. Level up, choose divine upgrades, and test your skills in Charon’s labyrinth.

## Features

- Infinite procedural map with spatial index (fast collision checks)
- Axis-separated sliding collision for player/enemies (fluid movement)
- Camera-centered viewport; all rendering at camera offset
- Modular OOP design: Game, Player, Enemy, WaveManager, Upgrade, UI
- Diverse Greek-themed upgrades (ZeusBolt, ArtemisArrow, PoseidonWave, AthenaShield, DionysusVine, HermesBoots, IncreaseMaxHealth, IncreaseDamage)
- One-shot upgrades for instant effects (speed, health, damage)
- Robust test coverage (46 tests, pytest)
- Greek myth themed art, UI, and overlays
- Coin and XP drop system, main menu, HUD, upgrade picker, game over/restart

## Installation

1. Clone this repo:  
   `git clone <repo-url>`  
2. Change to project folder:  
   `cd vampire_survivors_clone`
3. Create and activate venv (if not present):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
4. Install dependencies:
   ```bash
   pip install pygame pytest black flake8
   ```

## Running the Game

```
python main.py
```

## Testing & Linting

- Run all tests:
  ```
  pytest
  ```
- Lint & format checks:
  ```
  flake8 .
  black --check .
  ```
- Auto-format:
  ```
  black .
  ```

## Project Structure

```
main.py                      - Main game loop, orchestration
game/
  player.py                  - Player class, upgrades, movement
  enemy.py                   - Enemy classes, pursuit AI
  map.py                     - Procedural map, camera, spatial index
  wave_manager.py            - Wave spawning, scaling
  upgrade.py                 - Divine blessings and effects
  ui.py                      - HUD, overlays, menus
  ...
assets/                      - Sprites, sounds, story files
tests/                       - Pytest tests for all modules
AGENTS.md                    - Agent roles and OOP module guide
PROJECT_PLAN.md              - Roadmap and technical design
STATUS_UPDATE.md             - Progress and session history
LORE_STYLE.md                - Narrative and art style lore
```

## Greek Myth Theme & Modularity

- All upgrades, enemies, and environments are designed around ancient Greek mythology.
- Modular agents (Player, Enemy, Wave, Upgrade, UI, Map, Art FX, QA) collaborate via OOP interfaces for extensibility.

## Contribute

- Fork and PRs welcome; see AGENTS.md for coding conventions
- Do not commit external or proprietary art/sounds—use open source or original creations

## License

_Coming soon_
