import random
from itertools import combinations
from pathlib import Path

from cards import make_deck, parse_cards
from evaluator import evaluate, evaluate_5
from lookup import clear_table, combo_rank, ensure_table, score_five


def test_combo_rank_is_unique_for_the_first_hands():
    assert combo_rank([0, 1, 2, 3, 4]) == 0
    assert combo_rank([0, 1, 2, 3, 5]) == 1
    assert combo_rank([47, 48, 49, 50, 51]) == 2_598_959


def test_lookup_matches_evaluate_five_on_known_and_random_hands(tmp_path):
    path = tmp_path / "five_card_ranks.bin"
    clear_table()
    ensure_table(path)

    known = [
        parse_cards("Ts Js Qs Ks As"),
        parse_cards("As 2s 3s 4s 5s"),
        parse_cards("8s 8h 8d 4c 4s"),
        parse_cards("As Kh Qd Jc 9s"),
    ]
    for hand in known:
        assert score_five(hand, path) == evaluate_5(hand)

    rng = random.Random(1)
    deck = make_deck()
    for _ in range(40):
        five = rng.sample(deck, 5)
        seven = rng.sample(deck, 7)
        assert score_five(five, path) == evaluate_5(five)
        looked = max(score_five(list(combo), path) for combo in combinations(seven, 5))
        direct = max(evaluate_5(list(combo)) for combo in combinations(seven, 5))
        assert looked == direct


def test_default_table_path_is_created_under_data():
    clear_table()
    table = ensure_table()
    assert len(table) == 2_598_960
    assert Path("data/five_card_ranks.bin").exists()
    seven = parse_cards("2c 2d 2h 2s 3c As Kd")
    assert evaluate(seven) == evaluate_5(parse_cards("2c 2d 2h 2s As"))