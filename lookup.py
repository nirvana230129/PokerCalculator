"""Five-card score table built from the current ``evaluate_5``.

Every ``C(52, 5)`` hand is scored once. The index is the combinatorial number of
the five card ids ``0..51``. Later lookups return that packed score without
classifying the hand again.
"""

from __future__ import annotations

import array
import math
from itertools import combinations
from pathlib import Path

from cards import Card, make_deck

TABLE_SIZE = math.comb(52, 5)
DEFAULT_PATH = Path(__file__).resolve().parent / "data" / "five_card_ranks.bin"

_TABLE: array.array | None = None
_CHOOSE = [[0] * 6 for _ in range(53)]
for n in range(53):
    _CHOOSE[n][0] = 1
    for k in range(1, min(n, 5) + 1):
        _CHOOSE[n][k] = _CHOOSE[n - 1][k - 1] + _CHOOSE[n - 1][k]


def combo_rank(card_ids: list[int]) -> int:
    """Map five sorted card ids to a unique index in ``0 .. C(52, 5) - 1``."""
    rank = 0
    for i, card_id in enumerate(sorted(card_ids)):
        rank += _CHOOSE[card_id][i + 1]
    return rank


def _score_path(path: Path | None = None) -> Path:
    return Path(path) if path is not None else DEFAULT_PATH


def build_table(path: Path | None = None) -> array.array:
    """Score every five-card hand with ``evaluate_5`` and write the binary table."""
    from evaluator import evaluate_5

    table = array.array("I", [0]) * TABLE_SIZE
    deck = make_deck()
    for combo in combinations(deck, 5):
        ids = [int(card) for card in combo]
        table[combo_rank(ids)] = evaluate_5(list(combo))
    target = _score_path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    with target.open("wb") as handle:
        table.tofile(handle)
    global _TABLE
    _TABLE = table
    return table


def load_table(path: Path | None = None) -> array.array:
    """Load a previously built table into memory."""
    source = _score_path(path)
    table = array.array("I")
    with source.open("rb") as handle:
        table.fromfile(handle, TABLE_SIZE)
    global _TABLE
    _TABLE = table
    return table


def ensure_table(path: Path | None = None) -> array.array:
    """Return the in-memory table, loading or building it when needed."""
    global _TABLE
    if _TABLE is not None and path is None:
        return _TABLE
    source = _score_path(path)
    if source.exists() and source.stat().st_size == TABLE_SIZE * 4:
        return load_table(source)
    return build_table(source)


def score_five(cards: list[Card], path: Path | None = None) -> int:
    """Return the packed score of exactly five cards from the lookup table.

    Raises:
        ValueError: the list does not contain five cards.
    """
    if len(cards) != 5:
        raise ValueError(f"Invalid number of cards: it must be 5, not {len(cards)}")
    table = ensure_table(path)
    return table[combo_rank([int(card) for card in cards])]


def clear_table() -> None:
    """Drop the in-memory table. Used by tests."""
    global _TABLE
    _TABLE = None
