import random

import pytest

from cards import parse_cards
from combo import unpack
from evaluator import HAND_NAMES, HandCategory, compare, describe_hand, evaluate, evaluate_5, hand_category


def hand(*names: str):
    cards = parse_cards(" ".join(names))
    random.shuffle(cards)
    return cards


def packed(category: int, *kickers: int):
    return (category, *kickers, *([0] * (5 - len(kickers))))


def got(cards):
    return unpack(evaluate_5(cards))


def test_every_category_and_its_kickers():
    assert got(hand("Ts", "Js", "Qs", "Ks", "As")) == packed(9)
    assert got(hand("As", "2s", "3s", "4s", "5s")) == packed(8, 3)
    assert got(hand("5c", "6c", "7c", "8c", "9c")) == packed(8, 7)
    assert got(hand("Ks", "Kh", "Kd", "Kc", "2s")) == packed(7, 11, 0)
    assert got(hand("Ks", "Kh", "Kd", "Kc", "As")) == packed(7, 11, 12)
    assert got(hand("8s", "8h", "8d", "4c", "4s")) == packed(6, 6, 2)
    assert got(hand("4s", "4h", "4d", "8c", "8s")) == packed(6, 2, 6)
    assert got(hand("2s", "5s", "9s", "Js", "As")) == packed(5, 12, 9, 7, 3, 0)
    assert got(hand("Ac", "2d", "3s", "4h", "5c")) == packed(4, 3)
    assert got(hand("Tc", "Jd", "Qs", "Kh", "Ac")) == packed(4, 12)
    assert got(hand("5c", "6d", "7s", "8h", "9c")) == packed(4, 7)
    assert got(hand("Qs", "Qh", "Qd", "2c", "7s")) == packed(3, 10, 5, 0)
    assert got(hand("2s", "2h", "2d", "3c", "7s")) == packed(3, 0, 5, 1)
    assert got(hand("Js", "Jh", "8d", "8c", "2s")) == packed(2, 9, 6, 0)
    assert got(hand("3s", "3h", "2d", "2c", "As")) == packed(2, 1, 0, 12)
    assert got(hand("As", "Ah", "Kd", "Qc", "Js")) == packed(1, 12, 11, 10, 9)
    assert got(hand("5s", "5h", "7d", "8c", "9s")) == packed(1, 3, 7, 6, 5)
    assert got(hand("As", "Kh", "Qd", "Jc", "9s")) == packed(0, 12, 11, 10, 9, 7)
    assert got(hand("As", "2h", "3d", "4c", "6s")) == packed(0, 12, 4, 2, 1, 0)


def test_compare_uses_category_then_kickers():
    wheel_sf = evaluate_5(parse_cards("As 2s 3s 4s 5s"))
    royal = evaluate_5(parse_cards("Ts Js Qs Ks As"))
    assert compare(wheel_sf, royal) == -1
    assert compare(royal, wheel_sf) == 1
    assert compare(royal, evaluate_5(parse_cards("As Ks Qs Js Ts"))) == 0
    assert compare(
        evaluate_5(parse_cards("8s 8h 8d 4c 4s")),
        evaluate_5(parse_cards("2s 5s 9s Js As")),
    ) == 1
    assert compare(
        evaluate_5(parse_cards("2s 2h 2d 2c As")),
        evaluate_5(parse_cards("2s 2h 2d 2c 3s")),
    ) == 1
    assert compare(
        evaluate_5(parse_cards("As Ah Kd Kc 2s")),
        evaluate_5(parse_cards("Qs Qh Kd Kc 2s")),
    ) == 1
    assert compare(
        evaluate_5(parse_cards("Ts 8c 6d 4h 2c")),
        evaluate_5(parse_cards("9s 8c 6d 4h 2c")),
    ) == 1


def test_evaluate_picks_the_best_five_from_six_or_seven():
    seven = parse_cards("2c 2d 2h 2s 3c As Kd")
    assert evaluate(seven) == evaluate_5(parse_cards("2c 2d 2h 2s As"))
    assert hand_category(evaluate(seven)) == HandCategory.FOUR_OF_A_KIND

    full = parse_cards("Ah Ad Ac Kd Kc Qs 2c")
    assert unpack(evaluate(full)) == packed(6, 12, 11)
    assert hand_category(evaluate(full)) == HandCategory.FULL_HOUSE

    straight = parse_cards("2c 3d 4h 5s 9c 6d Kh")
    assert evaluate(straight) == evaluate_5(parse_cards("2c 3d 4h 5s 6d"))

    flush = parse_cards("As 2s 5s 9s Js Kd")
    assert evaluate(flush) == evaluate_5(parse_cards("As 2s 5s 9s Js"))
    assert hand_category(evaluate(parse_cards("Ts Js Qs Ks As 2h"))) == HandCategory.ROYAL_FLUSH

    five = parse_cards("As Kh Qd Jc 9s")
    assert evaluate(five) == evaluate_5(five)


def test_describe_hand_and_category_names():
    full_house = evaluate_5(parse_cards("8s 8h 8d 4c 4s"))
    assert describe_hand(full_house) == "6: 6, 2, 0, 0, 0"
    assert set(HAND_NAMES) == set(HandCategory)


@pytest.mark.parametrize("cards", ["As Kh", "As Kh Qd Jc"])
def test_evaluate_requires_at_least_five_cards(cards):
    with pytest.raises(ValueError):
        evaluate_5(parse_cards(cards))
    if len(parse_cards(cards)) < 5:
        with pytest.raises(ValueError):
            evaluate(parse_cards(cards))
