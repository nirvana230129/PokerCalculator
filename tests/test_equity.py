import random

import pytest

from cards import cards_to_str, parse_cards
from equity import equity_vs_random, monte_carlo_equity, single_trial


def test_single_trial_splits_a_shared_royal_and_awards_the_nuts():
    rng = random.Random(0)
    hero = parse_cards("As Ah")
    royal = parse_cards("Ts Js Qs Ks As")
    assert single_trial(parse_cards("2c 3d"), royal, 1, rng) == 0.5
    assert single_trial(parse_cards("2c 3d"), royal, 2, rng) == 1 / 3
    assert single_trial(parse_cards("2c 3d"), royal, 0, rng) == 1

    nuts = parse_cards("Ad Ac 2c 7d 9s")
    assert single_trial(hero, nuts, 2, rng) == 1

    kept = parse_cards("Qd 7c 2s")
    single_trial(hero, kept, 1, rng)
    assert cards_to_str(kept) == "Qd 7c 2s"
    assert single_trial(hero, parse_cards("Kd 7c 2s 9h"), 1, rng) in (0, 0.5, 1)


@pytest.mark.parametrize(
    "hero, board, opponents",
    [
        ("As", "", 1),
        ("As Ah", "Qd", 1),
        ("As Ah", "Qd 7c", 1),
        ("As Ah As", "Qd 7c 2s", 1),
        ("As Ah", "Qd 7c 2s", -1),
        ("As Ah", "As 7c 2s", 1),
    ],
)
def test_single_trial_rejects_a_malformed_deal(hero, board, opponents):
    with pytest.raises(ValueError):
        single_trial(parse_cards(hero), parse_cards(board), opponents, random.Random(0))


def test_monte_carlo_reports_fractions_and_repeats_with_the_same_seed():
    hero = parse_cards("As Ah")
    nuts = parse_cards("Ad Ac 2c 7d 9s")
    result = monte_carlo_equity(hero, nuts, 1, n=50, seed=1)
    assert result.equity == 1
    assert (result.win, result.tie, result.lose) == (1, 0, 0)
    assert result.samples == 50
    assert result.exact is False
    assert result.elapsed >= 0

    royal = parse_cards("Ts Js Qs Ks As")
    chop = monte_carlo_equity(parse_cards("2c 3d"), royal, 1, n=50, seed=1)
    assert chop.equity == 0.5
    assert (chop.win, chop.tie, chop.lose) == (0, 1, 0)

    aces = monte_carlo_equity(hero, [], 1, n=4_000, seed=1)
    assert abs(aces.equity - 0.85) < 0.02
    assert abs(aces.equity - (aces.win + aces.tie / 2)) < 1e-12
    assert abs(aces.win + aces.tie + aces.lose - 1) < 1e-12
    again = equity_vs_random(hero, [], 1, n=4_000, seed=1)
    assert again.equity == aces.equity
