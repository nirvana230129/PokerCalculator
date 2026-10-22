"""Hero equity against opponent ranges.

Monte Carlo samples random hands from each range. Exact enumeration walks every
legal hand and every missing board card. ``calculate_equity`` picks the method
from an upper bound on the number of runouts.
"""

import math
import random
import time
from dataclasses import dataclass
from itertools import combinations, product

from tqdm import tqdm

from cards import Card, make_deck, remove_known
from deck import Deck
from evaluator import compare, evaluate
from ranges import Range


@dataclass
class EquityResult:
    """Result of an equity calculation.

    ``equity`` is the average pot share. ``win``, ``tie``, and ``lose`` are trial shares:
    the whole pot, a split the hero is part of, and a loss. Heads-up,
    ``equity == win + tie / 2``. ``samples`` is the number of runouts counted.
    ``exact`` is ``True`` when every legal runout was counted. ``elapsed`` is the
    running time in seconds.
    """
    equity: float
    win: float
    tie: float
    lose: float
    samples: int
    exact: bool
    elapsed: float


def _validate(hero: list[Card], board: list[Card]) -> None:
    if len(hero) != 2 or len(board) not in (0, 3, 4, 5):
        raise ValueError(f"Hero must have 2 cards and board 0, 3, 4 or 5, not {len(hero)} and {len(board)}")
    if len(set(hero + board)) != len(hero) + len(board):
        raise ValueError("Hero and board contain duplicate cards")


def _pot_share(hero: list[Card], board: list[Card], opponents: list[list[Card]]) -> float:
    """Return the hero's share of a fully dealt board.

    The share is ``0`` when anyone beats the hero, ``1`` when the hero wins alone,
    and ``1 / k`` when ``k`` players including the hero split the pot.
    """
    hero_score = evaluate(hero + board)
    equal = 0
    for opponent_cards in opponents:
        opponent_score = evaluate(opponent_cards + board)
        if compare(opponent_score, hero_score) > 0:
            return 0.0
        if compare(opponent_score, hero_score) == 0:
            equal += 1
    if equal == 0:
        return 1.0
    return 1.0 / (equal + 1)


def _deal_hands(hero: list[Card], board: list[Card], opp_ranges: list[Range], rng: random.Random):
    """Deal one hand from each range, skipping cards already used by earlier players."""
    blockers = hero + board
    hands = []
    for opp_range in opp_ranges:
        choices = opp_range.combos(blockers)
        if not choices:
            return None
        hand = rng.choice(choices)
        hands.append(hand)
        blockers.extend(hand)
    return hands


def _single_trial(hero: list[Card], board: list[Card], opponents: list[list[Card]], rng: random.Random = random) -> float:
    """Fill the board at random and return the hero's pot share for these hands.

    Raises:
        ValueError: the hero or board has the wrong length, or any known card is repeated.
    """
    _validate(hero, board)
    known = hero + board + [card for hand in opponents for card in hand]
    if len(set(known)) != len(known):
        raise ValueError("Known cards overlap")
    deck = Deck(rng=rng)
    deck.remove(known)
    full_board = board + deck.draw(5 - len(board))
    return _pot_share(hero, full_board, opponents)


def monte_carlo_equity(hero: list[Card], board: list[Card], opp_ranges: list[Range], n: int = 100_000, seed: int | None = None) -> EquityResult:
    """Average ``n`` deals from ``opp_ranges``.

    Each opponent is dealt from the combinations that avoid the hero, the board,
    and hands already dealt to earlier opponents. ``seed`` makes the same arguments
    produce the same result. ``exact`` in the result is always ``False``.
    """
    _validate(hero, board)
    rng = random.Random(seed)
    total_result = 0.0
    wins = ties = loses = 0
    start_time = time.time()
    dealt = 0
    for _ in tqdm(range(n)):
        while True:
            opponents = _deal_hands(hero, board, opp_ranges, rng)
            if opponents is not None:
                break
        result = _single_trial(hero, board, opponents, rng)
        dealt += 1
        if result == 0:
            loses += 1
        elif result == 1:
            wins += 1
        else:
            ties += 1
        total_result += result
    elapsed = time.time() - start_time
    return EquityResult(total_result / n, wins / n, ties / n, loses / n, dealt, False, elapsed)


def exact_equity(hero: list[Card], board: list[Card], opp_ranges: list[Range]) -> EquityResult:
    """Average every pair of opponent hands and every missing board card.

    Hands that share a card with the hero, the board, or each other are skipped.
    On the river the board loop has one empty runout. ``exact`` is ``True``.

    Raises:
        ValueError: the deal is malformed, or no legal runout remains.
    """
    _validate(hero, board)
    known = hero + board
    range_combos = [opp.combos(known) for opp in opp_ranges]
    total_result = 0.0
    wins = ties = loses = 0
    n = 0
    start_time = time.time()
    for hands in product(*range_combos):
        flat = [card for hand in hands for card in hand]
        if len(set(flat)) != len(flat):
            continue
        unknown = remove_known(make_deck(), known + flat)
        for extra in combinations(unknown, 5 - len(board)):
            share = _pot_share(hero, board + list(extra), hands)
            total_result += share
            n += 1
            if share == 0:
                loses += 1
            elif share == 1:
                wins += 1
            else:
                ties += 1
    if n == 0:
        raise ValueError("No legal runouts for these ranges")
    elapsed = time.time() - start_time
    return EquityResult(total_result / n, wins / n, ties / n, loses / n, n, True, elapsed)


def expected_combinations(board: list[Card], opp_ranges: list[Range]) -> int:
    """Upper bound on exact runouts: board cards left times each range size.

    The bound ignores that ranges share cards, so it is a little high. It is only
    used to choose between exact enumeration and Monte Carlo.
    """
    board_left = 5 - len(board)
    unknown = 52 - 2 - len(board)
    total = math.comb(unknown, board_left)
    for opp_range in opp_ranges:
        total *= opp_range.size()
    return total


def equity_vs_random(hero, board, n_opponents, n=100_000, seed=None) -> EquityResult:
    """Equity against ``n_opponents`` players who hold uniformly random hands."""
    if n_opponents < 0:
        raise ValueError(f"Number of opponents must be non-negative, not {n_opponents}")
    opp_ranges = []
    for _ in range(n_opponents):
        opp_range = Range("22")
        opp_range.uniform()
        opp_ranges.append(opp_range)
    return monte_carlo_equity(hero, board, opp_ranges, n=n, seed=seed)


def calculate_equity(hero: list[Card], board: list[Card], opp_ranges: list[Range], mode: str = "auto", n: int = 100_000, seed: int | None = None) -> EquityResult:
    """Return exact equity, or Monte Carlo when the runout bound exceeds one million.

    ``mode`` is ``"auto"``, ``"exact"``, or ``"monte_carlo"``. ``n`` and ``seed`` apply
    only to the Monte Carlo path.
    """
    if mode not in ("auto", "monte_carlo", "exact"):
        raise ValueError(f"Unknown mode: {mode}")
    if mode == "exact" or (mode == "auto" and expected_combinations(board, opp_ranges) <= 1_000_000):
        return exact_equity(hero, board, opp_ranges)
    return monte_carlo_equity(hero, board, opp_ranges, n=n, seed=seed)


def all_hands_equity(board: list[Card], opp_ranges: list[Range], mode: str = "auto", n: int = 100_000, seed: int | None = None) -> dict[tuple[Card, Card], EquityResult]:
    """Equity of every concrete two-card hand that does not use a board card.

    ``Kh Qh`` and ``Kd Qd`` are separate entries: on a two-heart flop they are not the
    same hand. A combo that shares a card with ``board`` is left out. On the river
    there are ``C(47, 2) = 1081`` hands. ``mode``, ``n``, and ``seed`` are forwarded
    to ``calculate_equity`` for each hand.

    Raises:
        ValueError: the board length is not 0, 3, 4, or 5, or the board repeats a card.
    """
    if len(board) not in (0, 3, 4, 5):
        raise ValueError(f"Board must have 0, 3, 4 or 5 cards, not {len(board)}")
    if len(set(board)) != len(board):
        raise ValueError("Board contains duplicate cards")
    remaining = remove_known(make_deck(), board)
    return {
        combo: calculate_equity(list(combo), board, opp_ranges, mode=mode, n=n, seed=seed)
        for combo in combinations(remaining, 2)
    }
