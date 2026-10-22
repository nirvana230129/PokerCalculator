import pytest

from cards import Card
from ranges import Range, StartingHand


def test_starting_hand_normalizes_and_expands():
    assert str(StartingHand("AKs")) == "AKs"
    assert str(StartingHand("kAs")) == "AKs"
    assert str(StartingHand("QQ")) == "QQ"
    assert StartingHand("AAo") == StartingHand("AA")
    assert str(StartingHand("  AKs ")) == "AKs"
    assert len(StartingHand("AKs").to_combos()) == 4
    assert all(combo[0].suit == combo[1].suit for combo in StartingHand("AKs").to_combos())
    assert len(StartingHand("AKo").to_combos()) == 12
    assert all(combo[0].suit != combo[1].suit for combo in StartingHand("AKo").to_combos())
    queens = StartingHand("QQ").to_combos()
    assert len(queens) == 6
    assert all(combo[0] != combo[1] for combo in queens)


@pytest.mark.parametrize("text", ["AK", "A1s", "QQQ"])
def test_starting_hand_rejects_bad_text(text):
    with pytest.raises(ValueError):
        StartingHand(text)


def test_range_plus_and_minus_keep_the_hand_shape():
    pairs = Range("22+")
    assert len(pairs) == 13
    assert str(pairs).split()[0] == "22"
    assert str(pairs).split()[-1] == "AA"

    assert [str(hand) for hand in Range("A2s+")] == [
        "A2s", "A3s", "A4s", "A5s", "A6s", "A7s", "A8s", "A9s", "ATs", "AJs", "AQs", "AKs"
    ]
    assert [str(hand) for hand in Range("KTo+")] == ["KTo", "KJo", "KQo"]
    assert Range("KQo+").hands == [StartingHand("KQo")]

    assert [str(hand) for hand in Range("JJ-99")] == ["99", "TT", "JJ"]
    assert [str(hand) for hand in Range("99-JJ")] == ["99", "TT", "JJ"]
    assert [str(hand) for hand in Range("AQs-ATs")] == ["ATs", "AJs", "AQs"]


def test_range_string_deduplicates_and_combos_respect_blockers():
    opened = Range("22+,A2s+, KQo, AKs, AKs")
    assert opened.weight == 1
    assert StartingHand("AA") in list(opened)
    assert StartingHand("A2s") in opened.hands
    assert StartingHand("KQo") in opened.hands
    assert StartingHand("A2o") not in opened.hands
    assert opened.hands.count(StartingHand("AKs")) == 1

    aks = Range("AKs")
    assert aks.size() == 4
    assert aks.size([Card("A", "h")]) == 3
    blocked = {tuple(str(card) for card in combo) for combo in aks.combos([Card("A", "h")])}
    assert ("Ah", "Kh") not in blocked

    full = Range("22")
    full.uniform()
    assert len(full) == 169
    assert full.size() == 1326


@pytest.mark.parametrize("text", ["AK", "A1s", "22-AKs", "AKs-KQo"])
def test_range_rejects_bad_tokens(text):
    with pytest.raises(ValueError):
        Range(text)
