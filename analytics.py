"""Hand-grid helpers for the equity page charts."""

from __future__ import annotations

from cards import Card
from equity import calculate_equity, equity_vs_random
from precompute import _TABLES, lookup_preflop
from ranges import Range, StartingHand

GRID_RANKS = "AKQJT98765432"
GRID_SAMPLE_CAP = 500


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


def _grid_samples(board: list[Card], mode: str, n: int) -> tuple[str, int]:
    """Pick mode and sample count so a 169-hand grid stays interactive."""
    samples = max(1, min(n, GRID_SAMPLE_CAP))
    if not board:
        return "monte_carlo", samples
    if mode == "monte_carlo":
        return "monte_carlo", samples
    return mode, samples


def _first_live_combo(name: str, blocked: set[Card]) -> list[Card] | None:
    """First concrete combo of ``name`` that does not use a blocked card."""
    for combo in StartingHand(name).to_combos():
        if not any(card in blocked for card in combo):
            return combo
    return None


def hand_grid(
    board: list[Card],
    opp_ranges: list[Range] | None = None,
    n_opponents: int | None = None,
    mode: str = "auto",
    n: int = 500,
    seed: int | None = None,
) -> dict:
    """Equity of each of the 169 canonical hands against the given opponents.

    One live concrete combo stands for each cell. The cell is empty only when
    every combo of that hand uses a board card. Preflop against a range uses
    Monte Carlo with at most ``GRID_SAMPLE_CAP`` samples per cell.
    """
    if opp_ranges is None and n_opponents is None:
        raise ValueError("Provide villain ranges or a random opponent count")
    if (
        not board
        and n_opponents is not None
        and (opp_ranges is None or len(opp_ranges) == 0)
        and n_opponents in _TABLES
    ):
        return hand_grid_from_preflop(n_opponents)

    grid_mode, samples = _grid_samples(board, mode, n)
    values = empty_grid_values()
    blocked = set(board)
    for row in range(13):
        for col in range(13):
            name = grid_hand_name(row, col)
            hero = _first_live_combo(name, blocked)
            if hero is None:
                values[name] = None
                continue
            hand_seed = None if seed is None else seed + row * 13 + col
            if n_opponents is not None and (opp_ranges is None or len(opp_ranges) == 0):
                result = equity_vs_random(hero, board, n_opponents, n=samples, seed=hand_seed)
            else:
                result = calculate_equity(
                    hero,
                    board,
                    list(opp_ranges or []),
                    mode=grid_mode,
                    n=samples,
                    seed=hand_seed,
                )
            values[name] = result.equity
    return {
        "ranks": list(GRID_RANKS),
        "values": values,
        "source": "canonical_169",
    }


def hand_grid_from_board(
    board: list[Card],
    opp_ranges: list[Range],
    mode: str = "auto",
    n: int = 500,
    seed: int | None = None,
) -> dict:
    """Compatibility wrapper: 169-hand grid against explicit ranges."""
    return hand_grid(board, opp_ranges=opp_ranges, mode=mode, n=n, seed=seed)
