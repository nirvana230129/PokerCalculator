"""Saved preflop equity for the 169 canonical hands.

Preflop against random opponents is expensive, and the answer for a hand such as
``AA`` barely changes between runs. ``build_preflop_table`` simulates it once.
``lookup_preflop`` reads that result and does not deal again.
"""

import json
from pathlib import Path

from equity import EquityResult, equity_vs_random
from ranges import Range, StartingHand

_TABLES: dict[int, dict[str, EquityResult]] = {}


def _canonical_hands() -> list[StartingHand]:
    ranks = Range("22")
    ranks.uniform()
    return list(ranks)


def build_preflop_table(n_opponents: int, iterations: int, seed: int | None = None) -> dict[str, EquityResult]:
    """Simulate every canonical hand against ``n_opponents`` random hands.

    One concrete combo stands for the hand: before the flop, the suits do not
    change equity against random opponents. The result is kept in memory for
    ``lookup_preflop``. ``seed`` makes the table reproducible.

    Raises:
        ValueError: ``n_opponents`` is negative or ``iterations`` is below 1.
    """
    if n_opponents < 0:
        raise ValueError(f"Number of opponents must be non-negative, not {n_opponents}")
    if iterations < 1:
        raise ValueError(f"Iterations must be at least 1, not {iterations}")
    table: dict[str, EquityResult] = {}
    for index, hand in enumerate(_canonical_hands()):
        hero = hand.to_combos()[0]
        hand_seed = None if seed is None else seed + index
        table[str(hand)] = equity_vs_random(hero, [], n_opponents, n=iterations, seed=hand_seed)
    _TABLES[n_opponents] = table
    return table


def save_table(path: str | Path, n_opponents: int) -> None:
    """Write the in-memory table for ``n_opponents`` as JSON.

    Raises:
        KeyError: that table has not been built or loaded.
    """
    table = _TABLES[n_opponents]
    payload = {
        "n_opponents": n_opponents,
        "hands": {name: result.__dict__ for name, result in table.items()},
    }
    Path(path).write_text(json.dumps(payload), encoding="utf-8")


def load_table(path: str | Path) -> dict[str, EquityResult]:
    """Read a JSON table into memory and return it, keyed by hand name."""
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    table = {name: EquityResult(**row) for name, row in payload["hands"].items()}
    _TABLES[payload["n_opponents"]] = table
    return table


def lookup_preflop(hand: str | StartingHand, n_opponents: int) -> EquityResult:
    """Return the stored equity of one canonical hand.

    ``"aa"`` and ``"AA"`` name the same cell. This does not run a simulation.

    Raises:
        KeyError: no table for this opponent count is in memory, or the hand is absent.
        ValueError: ``hand`` is not a canonical starting hand.
    """
    name = str(hand if isinstance(hand, StartingHand) else StartingHand(hand))
    try:
        return _TABLES[n_opponents][name]
    except KeyError:
        raise KeyError(f"No stored preflop equity for {name} against {n_opponents} opponents") from None
