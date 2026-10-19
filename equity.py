"""Эквити героя против случайных рук оппонентов.

Считается Монте-Карло: недостающий борд и руки оппонентов сдаются заново много раз,
доля банка героя усредняется.
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
    """Итог расчёта эквити.

    ``equity`` — средняя доля банка. ``win``, ``tie`` и ``lose`` — доли розыгрышей:
    весь банк, дележ, в котором герой участвует, и проигрыш. В игре один на один
    ``equity == win + tie / 2``. ``samples`` — число розыгрышей. ``exact`` равен
    ``False``, пока результат получен выборкой, а не полным перебором. ``elapsed`` —
    длительность расчёта в секундах.
    """

    equity: float
    win: float
    tie: float
    lose: float
    samples: int
    exact: bool
    elapsed: float


def single_trial(hero: list[Card], board: list[Card], n_opponents: int, rng: random.Random = random) -> float:
    """Разыграть одну случайную раздачу и вернуть долю банка героя.

    Борд добирается до пяти карт, каждому оппоненту сдаются две карты из оставшейся
    колоды. Доля равна ``0``, если кто-то старше героя, ``1``, если герой один
    победитель, и ``1 / k``, если банк делят ``k`` игроков вместе с героем.

    Raises:
        ValueError: у героя не две карты, длина борда не 0, 3, 4 или 5,
            оппонентов меньше нуля или известные карты повторяются.
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
    """Усреднить ``n`` вызовов ``single_trial``.

    ``seed`` фиксирует генератор и делает повторный вызов с теми же аргументами
    воспроизводимым. ``exact`` в результате всегда ``False``.
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
    """Посчитать эквити против случайных рук. Сейчас это то же, что ``monte_carlo_equity``."""
    return monte_carlo_equity(hero, board, n_opponents, n=n, seed=seed)
