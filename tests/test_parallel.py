import pytest

from cards import parse_cards
from equity import EquityResult
from parallel import merge_results, monte_carlo_parallel
from ranges import Range


def test_merge_results_weights_by_samples():
    left = EquityResult(1.0, 1.0, 0.0, 0.0, 10, False, 0.1)
    right = EquityResult(0.0, 0.0, 0.0, 1.0, 30, False, 0.2)
    merged = merge_results([left, right])
    assert merged.samples == 40
    assert merged.equity == pytest.approx(0.25)
    assert merged.win == pytest.approx(0.25)
    assert merged.lose == pytest.approx(0.75)
    assert merged.tie == 0
    assert merged.exact is False
    assert merged.elapsed == pytest.approx(0.3)


def test_merge_results_rejects_an_empty_list():
    with pytest.raises(ValueError):
        merge_results([])


def test_monte_carlo_parallel_matches_single_worker_sample_count():
    hero = parse_cards("As Ah")
    result = monte_carlo_parallel(hero, [], [Range("KK")], n=40, seed=1, workers=2)
    assert result.samples == 40
    assert result.exact is False
    assert abs(result.equity - 0.82) < 0.2
    one = monte_carlo_parallel(hero, [], [Range("KK")], n=40, seed=1, workers=1)
    assert one.samples == 40
