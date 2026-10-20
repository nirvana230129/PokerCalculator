"""Hero equity against random opponent hands.

The estimate is Monte Carlo: the missing board cards and the opponents' hands are dealt
many times, and the hero's pot share is averaged.
"""

import time
from cards import Card
from deck import Deck
from evaluator import compare, evaluate
from tqdm import tqdm
import random
from dataclasses import dataclass


@dataclass
class EquityResult:
    """Result of an equity calculation.

    ``equity`` is the average pot share. ``win``, ``tie``, and ``lose`` are trial shares:
    the whole pot, a split the hero is part of, and a loss. Heads-up,
    ``equity == win + tie / 2``. ``samples`` is the number of trials. ``exact`` stays
    ``False`` while the result comes from sampling rather than full enumeration.
    ``elapsed`` is the running time in seconds.
    """

    equity: float
    win: float
    tie: float
    lose: float
    samples: int
    exact: bool
    elapsed: float


def single_trial(hero: list[Card], board: list[Card], n_opponents: int, rng: random.Random = random) -> float:
    """Play one random deal and return the hero's pot share.

    The board is filled to five cards, and each opponent is dealt two cards from the
    remaining deck. The share is ``0`` when anyone beats the hero, ``1`` when the hero
    wins alone, and ``1 / k`` when ``k`` players including the hero split the pot.

    Raises:
        ValueError: the hero does not have two cards, the board length is not 0, 3, 4,
            or 5, the opponent count is negative, or known cards are duplicated.
    """
    if len(hero) != 2 or len(board) not in (0, 3, 4, 5):
        raise ValueError(f"Hero must have 2 cards and board 0, 3, 4 or 5, not {len(hero)} and {len(board)}")
    if n_opponents < 0:
        raise ValueError(f"Number of opponents must be non-negative, not {n_opponents}")
    if len(set(hero + board)) != len(hero) + len(board):
        raise ValueError("Hero and board contain duplicate cards")
    deck = Deck(rng=rng)
    deck.remove(hero + board)
    board = board + deck.draw(5 - len(board))
    hero_score = evaluate(hero + board)
    equal = 0
    for _ in range(n_opponents):
        opponent = deck.draw(2)
        opponent_score = evaluate(opponent + board)
        if compare(opponent_score, hero_score) > 0:
            return 0
        if compare(opponent_score, hero_score) == 0:
            equal += 1
    return 1 if equal == 0 else 1 / (equal + 1)

def monte_carlo_equity(hero, board, n_opponents, n=100_000, seed=None) -> EquityResult:
    """Average ``n`` calls to ``single_trial``.

    ``seed`` fixes the generator, so the same arguments produce the same result again.
    ``exact`` in the result is always ``False``.
    """
    rng = random.Random(seed)
    total_result = 0
    wins = ties = loses = 0
    start_time = time.time()
    for _ in tqdm(range(n)):
        result = single_trial(hero, board, n_opponents, rng)
        if result == 0:
            loses += 1
        elif result == 1:
            wins += 1
        else:
            ties += 1
        total_result += result
    elapsed = time.time() - start_time
    return EquityResult(total_result / n, wins / n, ties / n, loses / n, n, False, elapsed)


def equity_vs_random(hero, board, n_opponents, n=100_000, seed=None) -> EquityResult:
    """Equity against random hands. Currently the same calculation as ``monte_carlo_equity``."""
    return monte_carlo_equity(hero, board, n_opponents, n=n, seed=seed)
