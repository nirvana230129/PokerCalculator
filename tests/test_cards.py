import pytest

from cards import Card, cards_to_str, group_by_rank, group_by_suit, make_deck, parse_cards, remove_known


def test_card_identity_and_ordering():
    ace_spades = Card(12, 0)
    assert ace_spades == Card("A", "s") == Card("a", "S")
    assert str(ace_spades) == "As"
    assert repr(ace_spades) == "Card(As)"
    assert int(ace_spades) == 48
    assert ace_spades == 48
    assert ace_spades != Card("A", "h")
    assert ace_spades != "As"

    assert Card(0, 0) < Card(0, 1) < Card(1, 0)
    assert Card("2", "s") <= Card("2", "h") <= Card("2", "h")
    assert Card("K", "c") >= Card("Q", "s")
    assert hash(Card("A", "s")) == hash(Card(12, 0))
    assert len({Card("A", "s"), Card("a", "S"), Card("K", "h")}) == 2


@pytest.mark.parametrize(
    "rank, suit",
    [(13, 0), (-1, 0), (0, 4), ("1", "s"), ("A", "x"), ("As", "s")],
)
def test_card_rejects_invalid_rank_or_suit(rank, suit):
    with pytest.raises(ValueError):
        Card(rank, suit)


def test_deck_helpers_round_trip_and_filter():
    deck = make_deck()
    assert len(deck) == 52
    assert len(set(deck)) == 52
    assert cards_to_str(deck[:3]) == "2s 2h 2d"
    assert cards_to_str(deck[-1:]) == "Ac"

    hand = parse_cards("As Kh Qd")
    assert hand == [Card("A", "s"), Card("K", "h"), Card("Q", "d")]
    assert cards_to_str(hand) == "As Kh Qd"
    with pytest.raises(ValueError):
        parse_cards("AsKh")

    known = parse_cards("As Kh")
    rest = remove_known(deck, known)
    assert len(deck) == 52
    assert len(rest) == 50
    assert all(card not in rest for card in known)
    assert Card("Q", "d") in rest


def test_group_by_rank_and_suit():
    pairs = group_by_rank(parse_cards("As Ah Kd Kc 2s"))
    assert {len(cards) for cards in pairs.values()} == {2, 1}
    assert len(pairs[Card("A", "s").rank]) == 2
    assert len(pairs[Card("2", "c").rank]) == 1

    suits = group_by_suit(parse_cards("As Ks Qs Jd Td"))
    assert len(suits[Card("A", "s").suit]) == 3
    assert len(suits[Card("J", "d").suit]) == 2
    assert Card("K", "h").suit not in suits
