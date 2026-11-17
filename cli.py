"""Command-line entry for equity against ranges or random opponents."""

from __future__ import annotations

import argparse
import sys

from cards import cards_to_str, parse_cards
from equity import (
    EquityResult,
    all_hands_equity,
    calculate_equity,
    equity_vs_random,
    expected_combinations,
)
from parallel import monte_carlo_parallel
from ranges import Range


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Texas Hold'em equity calculator")
    parser.add_argument("--hero", help='Hero hole cards, for example "As Kh"')
    parser.add_argument("--board", default="", help='Board cards, for example "Qd 7c 2s"')
    parser.add_argument("--villain", help='Opponent range, for example "JJ+, AKs"')
    parser.add_argument("--opponents", type=int, help="Number of random opponents")
    parser.add_argument("--mode", choices=("auto", "exact", "monte_carlo"), default="auto")
    parser.add_argument("--samples", type=int, default=100_000, help="Monte Carlo trials")
    parser.add_argument("--seed", type=int, default=None, help="RNG seed for Monte Carlo")
    parser.add_argument("--workers", type=int, default=1, help="Process count for Monte Carlo")
    parser.add_argument(
        "--all-hands",
        action="store_true",
        help="Equity of every hole-card combo that avoids the board",
    )
    return parser


def format_result(result: EquityResult) -> str:
    method = "exact" if result.exact else "monte_carlo"
    return (
        f"equity={result.equity:.6f} "
        f"win={result.win:.6f} "
        f"tie={result.tie:.6f} "
        f"lose={result.lose:.6f} "
        f"samples={result.samples} "
        f"method={method} "
        f"elapsed={result.elapsed:.3f}s"
    )


def _parse_board(text: str):
    return parse_cards(text) if text.strip() else []


def _villain_ranges(text: str) -> list[Range]:
    return [Range(text)]


def _random_ranges(n_opponents: int) -> list[Range]:
    ranges = []
    for _ in range(n_opponents):
        opp = Range("22")
        opp.uniform()
        ranges.append(opp)
    return ranges


def _equity_for_ranges(hero, board, opp_ranges, mode: str, samples: int, seed: int | None, workers: int) -> EquityResult:
    use_monte = mode == "monte_carlo" or (
        mode == "auto" and expected_combinations(board, opp_ranges) > 1_000_000
    )
    if use_monte and workers > 1:
        return monte_carlo_parallel(hero, board, opp_ranges, n=samples, seed=seed, workers=workers)
    if mode == "exact" or not use_monte:
        return calculate_equity(hero, board, opp_ranges, mode=mode, n=samples, seed=seed)
    return monte_carlo_parallel(hero, board, opp_ranges, n=samples, seed=seed, workers=workers)


def run(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.villain is not None and args.opponents is not None:
        print("--villain and --opponents cannot be used together", file=sys.stderr)
        return 2
    if args.workers < 1:
        print("--workers must be at least 1", file=sys.stderr)
        return 2
    if args.samples < 1:
        print("--samples must be at least 1", file=sys.stderr)
        return 2

    try:
        board = _parse_board(args.board)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    if args.all_hands:
        if args.hero:
            print("--all-hands does not take --hero", file=sys.stderr)
            return 2
        if args.villain is not None:
            opp_ranges = _villain_ranges(args.villain)
        elif args.opponents is not None:
            if args.opponents < 0:
                print("--opponents must be non-negative", file=sys.stderr)
                return 2
            opp_ranges = _random_ranges(args.opponents)
        else:
            opp_ranges = []
        try:
            table = all_hands_equity(
                board,
                opp_ranges,
                mode=args.mode,
                n=args.samples,
                seed=args.seed,
            )
        except ValueError as exc:
            print(exc, file=sys.stderr)
            return 2
        for hand, result in sorted(table.items(), key=lambda item: item[1].equity, reverse=True):
            print(f"{cards_to_str(list(hand))}\t{format_result(result)}")
        return 0

    if not args.hero:
        print("--hero is required unless --all-hands is set", file=sys.stderr)
        return 2
    if args.villain is None and args.opponents is None:
        print("one of --villain or --opponents is required", file=sys.stderr)
        return 2

    try:
        hero = parse_cards(args.hero)
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    try:
        if args.opponents is not None:
            if args.opponents < 0:
                print("--opponents must be non-negative", file=sys.stderr)
                return 2
            if args.workers > 1:
                result = monte_carlo_parallel(
                    hero,
                    board,
                    _random_ranges(args.opponents),
                    n=args.samples,
                    seed=args.seed,
                    workers=args.workers,
                )
            else:
                result = equity_vs_random(hero, board, args.opponents, n=args.samples, seed=args.seed)
        else:
            result = _equity_for_ranges(
                hero,
                board,
                _villain_ranges(args.villain),
                args.mode,
                args.samples,
                args.seed,
                args.workers,
            )
    except ValueError as exc:
        print(exc, file=sys.stderr)
        return 2

    print(format_result(result))
    return 0


def main(argv: list[str] | None = None) -> None:
    raise SystemExit(run(argv))


if __name__ == "__main__":
    main()
