"""Simple JSON-backed save system for coins and relics.

API:
- load_save() -> dict: returns {'coins': int, 'relics': [str]}
- save_state(state: dict) -> None: atomically writes save.json

Migration: If save.json missing and coins.txt present, migrate coins into save.json
and create coins.txt.bak.
"""
import json
import os
from typing import Dict, Any

SAVE_PATH = "save.json"
COINS_TXT = "coins.txt"

def _default_state() -> Dict[str, Any]:
    return {"coins": 0, "relics": []}

def load_save() -> Dict[str, Any]:
    # Migrate from coins.txt if necessary
    if not os.path.exists(SAVE_PATH) and os.path.exists(COINS_TXT):
        try:
            with open(COINS_TXT, 'r') as f:
                coins = int(f.read().strip())
        except Exception:
            coins = 0
        state = _default_state()
        state["coins"] = coins
        try:
            save_state(state)
            # Backup old coins file
            try:
                os.replace(COINS_TXT, COINS_TXT + ".bak")
            except Exception:
                pass
        except Exception:
            pass
        return state

    if not os.path.exists(SAVE_PATH):
        return _default_state()

    try:
        with open(SAVE_PATH, 'r') as f:
            return json.load(f)
    except Exception:
        return _default_state()


def save_state(state: Dict[str, Any]) -> None:
    # Atomic write: write to temp then rename
    tmp = SAVE_PATH + ".tmp"
    with open(tmp, 'w') as f:
        json.dump(state, f, indent=2)
    try:
        os.replace(tmp, SAVE_PATH)
    except Exception:
        # Best-effort
        try:
            os.remove(SAVE_PATH)
        except Exception:
            pass
        os.replace(tmp, SAVE_PATH)
