"""Minimal relics system and shop helper.

Relic descriptor format:
- id: str
- name: str
- description: str
- cost: int
- apply(player): applies persistent effect to player on run start

Shop API:
- list_relics() -> list of descriptors
- purchase_relic(save_state, relic_id) -> bool (True if purchased)
"""
from typing import Dict, Any, List
from dataclasses import dataclass


@dataclass
class Relic:
    id: str
    name: str
    description: str
    cost: int

    def apply(self, player) -> None:
        """Apply persistent effect to player. Keep effects small and explicit."""
        if self.id == "tranq-sandals":
            # small permanent speed bonus
            player.speed = min(player.speed + 1, getattr(player, 'MAX_SPEED', 12))


RELICS: Dict[str, Relic] = {
    "tranq-sandals": Relic(
        id="tranq-sandals",
        name="Tranquil Sandals",
        description="Permanently increases move speed by +1.",
        cost=10,
    ),
}


def list_relics() -> List[Relic]:
    return list(RELICS.values())


def purchase_relic(save_state: Dict[str, Any], relic_id: str) -> bool:
    coins = save_state.get("coins", 0)
    if relic_id not in RELICS:
        return False
    if relic_id in save_state.get("relics", []):
        return False
    cost = RELICS[relic_id].cost
    if coins < cost:
        return False
    save_state["coins"] = coins - cost
    save_state.setdefault("relics", []).append(relic_id)
    return True
