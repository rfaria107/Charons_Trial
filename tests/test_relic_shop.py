import pytest
from game.relics import purchase_relic, RELICS


def test_purchase_relic_success(tmp_path):
    state = {"coins": 100, "relics": []}
    rid = next(iter(RELICS.keys()))
    ok = purchase_relic(state, rid)
    assert ok
    assert rid in state["relics"]
    assert state["coins"] == 100 - RELICS[rid].cost


def test_purchase_relic_insufficient_funds():
    state = {"coins": 0, "relics": []}
    rid = next(iter(RELICS.keys()))
    ok = purchase_relic(state, rid)
    assert not ok
    assert rid not in state["relics"]


def test_purchase_relic_double_prevention():
    state = {"coins": 100, "relics": []}
    rid = next(iter(RELICS.keys()))
    assert purchase_relic(state, rid)
    # Attempt second purchase
    before_coins = state["coins"]
    ok2 = purchase_relic(state, rid)
    assert not ok2
    assert state["coins"] == before_coins
