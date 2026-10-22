import math
import random

import pytest

from cards import cards_to_str, parse_cards
from equity import (
    _single_trial,
    calculate_equity,
    equity_vs_random,
    exact_equity,
    expected_combinations,
    monte_carlo_equity,
)
from ranges import Range


def test_fixed_hands_split_a_royal_and_award_quads():
    rng = random.Random(0)
    hero = parse_cards("As Ah")
    royal = parse_cards("Ts Js Qs Ks As")
    assert _single_trial(parse_cards("2c 3d"), royal, [parse_cards("4h 5d")], rng) == 0.5
    assert _single_trial(
        parse_cards("2c 3d"),
        royal,
        [parse_cards("4h 5d"), parse_cards("6h 7d")],
        rng,
    ) == pytest.approx(1 / 3)
    assert _single_trial(parse_cards("2c 3d"), royal, [], rng) == 1

    nuts = parse_cards("Ad Ac 2c 7d 9s")
    assert _single_trial(hero, nuts, [parse_cards("Kd Kc"), parse_cards("Qd Qc")], rng) == 1

    kept = parse_cards("Qd 7c 2s")
    _single_trial(hero, kept, [parse_cards("Kd Kc")], rng)
    assert cards_to_str(kept) == "Qd 7c 2s"


@pytest.mark.parametrize(
    "hero, board",
    [
        ("As", ""),
        ("As Ah", "Qd"),
        ("As Ah", "Qd 7c"),
        ("As Ah As", "Qd 7c 2s"),
        ("As Ah", "As 7c 2s"),
    ],
)
def test_single_trial_rejects_a_malformed_deal(hero, board):
    with pytest.raises(ValueError):
        _single_trial(parse_cards(hero), parse_cards(board), [], random.Random(0))


def test_single_trial_rejects_overlapping_hands():
    with pytest.raises(ValueError):
        _single_trial(
            parse_cards("As Ah"),
            parse_cards("2c 7d 9h 4s 3c"),
            [parse_cards("As Kd")],
            random.Random(0),
        )


def test_random_equity_matches_known_values_and_repeats():
    hero = parse_cards("As Ah")
    nuts = parse_cards("Ad Ac 2c 7d 9s")
    result = equity_vs_random(hero, nuts, 1, n=30, seed=1)
    assert result.equity == 1
    assert (result.win, result.tie, result.lose) == (1, 0, 0)
    assert result.samples == 30
    assert result.exact is False

    royal = parse_cards("Ts Js Qs Ks As")
    chop = equity_vs_random(parse_cards("2c 3d"), royal, 1, n=30, seed=1)
    assert chop.equity == 0.5
    assert (chop.win, chop.tie, chop.lose) == (0, 1, 0)

    aces = equity_vs_random(hero, [], 1, n=2_000, seed=1)
    assert abs(aces.equity - 0.85) < 0.03
    assert abs(aces.equity - (aces.win + aces.tie / 2)) < 1e-12
    again = equity_vs_random(hero, [], 1, n=2_000, seed=1)
    assert again.equity == aces.equity
    with pytest.raises(ValueError):
        equity_vs_random(hero, [], -1, n=1)


def test_exact_river_is_one_for_aces_against_kings_and_splits_a_royal():
    hero = parse_cards("As Ah")
    board = parse_cards("2c 7d 9h 4s 3c")
    kings = exact_equity(hero, board, [Range("KK")])
    assert kings.exact is True
    assert kings.equity == 1
    assert kings.samples == 6
    assert (kings.win, kings.tie, kings.lose) == (1, 0, 0)

    royal = parse_cards("Ts Js Qs Ks As")
    chop = exact_equity(parse_cards("2c 3d"), royal, [Range("54o")])
    assert chop.equity == 0.5
    assert chop.tie == 1
    assert chop.samples == 12


def test_exact_enumeration_skips_hands_that_share_a_card():
    board = parse_cards("2c 7d 9h 4s Jc")
    result = exact_equity(parse_cards("Qs Qh"), board, [Range("AKs"), Range("AKs")])
    assert result.samples == 12
    assert result.equity == 1


def test_monte_carlo_against_kings_is_near_the_known_value():
    result = monte_carlo_equity(parse_cards("As Ah"), [], [Range("KK")], n=4_000, seed=1)
    assert result.exact is False
    assert abs(result.equity - 0.82) < 0.03


def test_expected_combinations_and_auto_mode():
    river = parse_cards("2c 7d 9h 4s 3c")
    assert expected_combinations(river, [Range("KK")]) == 6
    assert expected_combinations([], [Range("KK")]) == math.comb(50, 5) * 6

    chosen = calculate_equity(parse_cards("As Ah"), river, [Range("KK")])
    assert chosen.exact is True
    assert chosen.equity == 1

    wide = calculate_equity(parse_cards("As Ah"), [], [Range("22")], mode="monte_carlo", n=20, seed=1)
    assert wide.exact is False
    assert wide.samples == 20
    with pytest.raises(ValueError):
        calculate_equity(parse_cards("As Ah"), river, [Range("KK")], mode="nope")
