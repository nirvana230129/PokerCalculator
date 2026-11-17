import math

import pytest

from cards import parse_cards
from cli import build_parser, format_result, run
from equity import EquityResult


def test_parser_accepts_the_documented_flags():
    args = build_parser().parse_args(
        ["--hero", "As Kh", "--board", "Qd 7c 2s", "--villain", "JJ+, AKs", "--mode", "auto"]
    )
    assert args.hero == "As Kh"
    assert args.board == "Qd 7c 2s"
    assert args.villain == "JJ+, AKs"
    assert args.mode == "auto"


def test_format_result_marks_exact_and_monte_carlo():
    exact = EquityResult(1.0, 1.0, 0.0, 0.0, 6, True, 0.01)
    assert "method=exact" in format_result(exact)
    sample = EquityResult(0.5, 0.4, 0.2, 0.4, 100, False, 1.5)
    assert "method=monte_carlo" in format_result(sample)


def test_cli_river_aces_beat_kings_exactly(capsys):
    code = run(
        [
            "--hero",
            "As Ah",
            "--board",
            "2c 7d 9h 4s 3c",
            "--villain",
            "KK",
            "--mode",
            "exact",
        ]
    )
    out = capsys.readouterr().out
    assert code == 0
    assert "equity=1.000000" in out
    assert "method=exact" in out


def test_cli_rejects_villain_with_opponents_and_all_hands_with_hero(capsys):
    assert run(["--hero", "As Ah", "--villain", "KK", "--opponents", "1"]) == 2
    assert "cannot be used together" in capsys.readouterr().err
    assert run(["--all-hands", "--hero", "As Ah", "--board", "2c 7d 9h"]) == 2
    assert "--all-hands does not take --hero" in capsys.readouterr().err


def test_cli_all_hands_skips_board_cards(capsys):
    board = "2c 7d 9h 4s 3c"
    code = run(["--board", board, "--all-hands", "--mode", "exact"])
    out = capsys.readouterr().out.strip().splitlines()
    assert code == 0
    assert len(out) == math.comb(47, 2)
    blocked = set(parse_cards(board))
    for line in out:
        hand = parse_cards(line.split("\t", 1)[0])
        assert len(hand) == 2
        assert blocked.isdisjoint(hand)
