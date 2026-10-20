"""A playing card and helpers for lists of cards.

Rank is an integer 0..12 in the order ``23456789TJQKA``. Suit is an integer 0..3 in the order ``shdc``.
"""

from functools import total_ordering


@total_ordering
class Card:
    """One card from the deck.

    Construct it from integers, ``Card(12, 0)``, or characters, ``Card("A", "s")``.
    ``int(card)`` is the index 0..51, equal to ``rank * 4 + suit``. Equality and
    hashing use that index, so cards can be stored in a ``set``.
    """

    SUITS = "shdc"
    RANKS = "23456789TJQKA"

    def __init__(self, rank, suit):
        """Accept a rank and a suit as integers or characters.

        Raises:
            ValueError: the rank or suit is not in the deck.
        """
        if isinstance(rank, int) and isinstance(suit, int) and 0 <= rank < 13 and 0 <= suit < 4:
            self.rank = rank
            self.suit = suit
        elif isinstance(rank, str) and isinstance(suit, str) and rank.upper() in self.RANKS and suit.lower() in self.SUITS:
            self.rank = self.RANKS.index(rank.upper())
            self.suit = self.SUITS.index(suit.lower())
        else:
            raise ValueError(f"Invalid rank or suit: {rank} {suit}")
        self.card = self.rank * 4 + self.suit

    def __lt__(self, other):
        if isinstance(other, Card):
            return self.card < other.card
        if isinstance(other, int):
            return self.card < other
        return NotImplemented
    
    def __eq__(self, other):
        if isinstance(other, Card):
            return self.card == other.card
        if isinstance(other, int):
            return self.card == other
        return NotImplemented
    
    def __hash__(self):
        return hash(self.card)
    
    def __str__(self):
        return f"{self.RANKS[self.rank]}{self.SUITS[self.suit]}"
    
    def __repr__(self):
        return f"Card({self.RANKS[self.rank]}{self.SUITS[self.suit]})"
    
    def __int__(self):
        return self.card


def make_deck() -> list[Card]:
    """Return a new 52-card deck, from ``2s`` through ``Ac``."""
    return [Card(rank, suit) for rank in range(13) for suit in range(4)]


def parse_cards(s: str) -> list[Card]:
    """Parse a space-separated string of cards.

    ``"As Kh Qd"`` yields three cards. A concatenated string such as ``"AsKh"`` is not parsed.
    """
    return [Card(rank, suit) for rank, suit in s.split()]


def cards_to_str(cards: list[Card]) -> str:
    """Join cards back into a string such as ``"As Kh Qd"``."""
    return ' '.join(str(card) for card in cards)


def remove_known(deck: list[Card], known: list[Card]) -> list[Card]:
    """Return a copy of the deck without the cards in ``known``. The original list is unchanged."""
    return [card for card in deck if card not in known]


def group_by_rank(cards: list[Card]) -> dict[int, list[Card]]:
    """Group cards by rank. The key is an integer 0..12."""
    ranks_dict: dict[int, list[Card]] = {}
    for card in cards:
        ranks_dict.setdefault(card.rank, []).append(card)
    return ranks_dict


def group_by_suit(cards: list[Card]) -> dict[int, list[Card]]:
    """Group cards by suit. The key is an integer 0..3 in ``shdc`` order."""
    suits_dict: dict[int, list[Card]] = {}
    for card in cards:
        suits_dict.setdefault(card.suit, []).append(card)
    return suits_dict