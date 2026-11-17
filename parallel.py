"""Split Monte Carlo equity across processes.

Each worker gets its own seed so the generators do not collide. Exact enumeration
is not parallelized here.
"""

import random
import time
from concurrent.futures import ProcessPoolExecutor

from cards import Card
from equity import EquityResult, monte_carlo_equity
from ranges import Range


def merge_results(results: list[EquityResult]) -> EquityResult:
    """Combine chunk results with weights equal to each chunk's ``samples``.

    ``exact`` stays ``False``: the merged value still comes from sampling.
    ``elapsed`` is the sum of the chunks' times (CPU), not wall-clock.
    """
    if not results:
        raise ValueError("No results to merge")
    total_samples = sum(result.samples for result in results)
    if total_samples == 0:
        raise ValueError("No samples to merge")
    equity = sum(result.equity * result.samples for result in results) / total_samples
    win = sum(result.win * result.samples for result in results) / total_samples
    tie = sum(result.tie * result.samples for result in results) / total_samples
    lose = sum(result.lose * result.samples for result in results) / total_samples
    elapsed = sum(result.elapsed for result in results)
    return EquityResult(equity, win, tie, lose, total_samples, False, elapsed)


def _chunk_sizes(n: int, workers: int) -> list[int]:
    base, rem = divmod(n, workers)
    return [base + (1 if i < rem else 0) for i in range(workers) if base + (1 if i < rem else 0) > 0]


def _run_chunk(args: tuple) -> EquityResult:
    hero, board, opp_ranges, n, seed = args
    return monte_carlo_equity(hero, board, opp_ranges, n=n, seed=seed)


def monte_carlo_parallel(
    hero: list[Card],
    board: list[Card],
    opp_ranges: list[Range],
    n: int = 100_000,
    seed: int | None = None,
    workers: int = 1,
) -> EquityResult:
    """Run ``monte_carlo_equity`` in ``workers`` processes and merge the chunks.

    Chunk ``i`` uses ``seed + i`` when ``seed`` is set. When ``seed`` is ``None``,
    a random base is chosen once, then each chunk gets ``base + i``. With
    ``workers == 1`` this is a plain ``monte_carlo_equity`` call.
    """
    if workers < 1:
        raise ValueError(f"workers must be at least 1, not {workers}")
    if n < 1:
        raise ValueError(f"n must be at least 1, not {n}")
    if workers == 1:
        return monte_carlo_equity(hero, board, opp_ranges, n=n, seed=seed)

    sizes = _chunk_sizes(n, workers)
    base = seed if seed is not None else random.randrange(2**31)
    tasks = [(hero, board, opp_ranges, size, base + i) for i, size in enumerate(sizes)]
    start = time.time()
    with ProcessPoolExecutor(max_workers=len(sizes)) as pool:
        chunks = list(pool.map(_run_chunk, tasks))
    merged = merge_results(chunks)
    return EquityResult(
        merged.equity,
        merged.win,
        merged.tie,
        merged.lose,
        merged.samples,
        False,
        time.time() - start,
    )
