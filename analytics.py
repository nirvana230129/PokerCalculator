"""Hand-grid helpers for the equity page charts."""

from __future__ import annotations

from cards import Card
from equity import all_hands_equity
from precompute import _TABLES, lookup_preflop
from ranges import Range

GRID_RANKS = "AKQJT98765432"


def grid_hand_name(row: int, col: int) -> str:
    """Canonical hand in the classic 13 by 13 matrix.

    Rows and columns are labeled ``A`` … ``2``. The diagonal is pairs, the upper
    triangle is suited, and the lower triangle is offsuit.
    """
    high = GRID_RANKS[row]
    low = GRID_RANKS[col]
    if row == col:
        return f"{high}{low}"
    if col > row:
        return f"{high}{low}s"
    return f"{low}{high}o"


def starting_hand_from_cards(first: Card, second: Card) -> str:
    """Canonical name of one concrete two-card combination."""
    ranks = Card.RANKS
    r1, r2 = ranks[first.rank], ranks[second.rank]
    if ranks.index(r1) < ranks.index(r2):
        r1, r2 = r2, r1
        first, second = second, first
    if r1 == r2:
        return f"{r1}{r2}"
    suited = first.suit == second.suit
    return f"{r1}{r2}{'s' if suited else 'o'}"


def empty_grid_values() -> dict[str, float | None]:
    return {grid_hand_name(row, col): None for row in range(13) for col in range(13)}


def hand_grid_from_preflop(n_opponents: int = 1) -> dict:
    """Fill the 13 by 13 grid from a stored preflop table.

    Raises:
        KeyError: no preflop table for this opponent count is loaded.
    """
    if n_opponents not in _TABLES:
        raise KeyError(f"No stored preflop equity against {n_opponents} opponents")
    values = empty_grid_values()
    for row in range(13):
        for col in range(13):
            name = grid_hand_name(row, col)
            values[name] = lookup_preflop(name, n_opponents).equity
    return {
        "ranks": list(GRID_RANKS),
        "values": values,
        "source": "preflop_table",
    }


def hand_grid_from_board(board: list[Card], opp_ranges: list[Range], mode: str = "auto", n: int = 1_000, seed: int | None = None) -> dict:
    """Average ``all_hands_equity`` into the 13 by 13 canonical matrix."""
    table = all_hands_equity(board, opp_ranges, mode=mode, n=n, seed=seed)
    buckets: dict[str, list[float]] = {}
    for hand, result in table.items():
        name = starting_hand_from_cards(hand[0], hand[1])
        buckets.setdefault(name, []).append(result.equity)
    values = empty_grid_values()
    for name, equities in buckets.items():
        values[name] = sum(equities) / len(equities)
    return {
        "ranks": list(GRID_RANKS),
        "values": values,
        "source": "all_hands",
    }
