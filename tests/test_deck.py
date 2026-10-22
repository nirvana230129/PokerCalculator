import random

import pytest

from cards import cards_to_str, parse_cards
from deck import Deck


def test_unshuffled_deck_deals_from_the_front_and_removes_known_cards():
    deck = Deck(shuffle=False)
    assert len(deck) == 52
    assert len(set(deck)) == 52
    assert cards_to_str(deck[:3]) == "2s 2h 2d"
    assert cards_to_str(deck[-1:]) == "Ac"
    assert str(deck).startswith("2s 2h")
    assert repr(deck) == "Deck(52 cards)"

    assert cards_to_str(deck.draw(2)) == "2s 2h"
    assert cards_to_str(deck[:3]) == "2d 2c 3s"
    assert cards_to_str(deck.remaining()) == str(deck)

    deck.remove(parse_cards("As Kh"))
    assert len(deck) == 48
    assert all(card not in deck for card in parse_cards("As Kh 2s 2h"))


def test_remake_restores_and_shuffles():
    deck = Deck(shuffle=False)
    deck.draw(2)
    deck.remove(parse_cards("As Kh"))
    deck.remake(shuffle=False)
    assert len(deck) == 52
    assert cards_to_str(deck[:2]) == "2s 2h"

    rng = random.Random(1)
    first = Deck(rng=rng)
    second = Deck(rng=random.Random(1))
    assert list(first) == list(second)

    before = deck[:]
    deck.remake()
    assert before != deck[:]


def test_draw_rejects_counts_outside_the_remaining_deck():
    deck = Deck(shuffle=False)
    assert deck.draw(0) == []
    with pytest.raises(ValueError):
        deck.draw(-1)
    with pytest.raises(ValueError):
        deck.draw(len(deck) + 1)
