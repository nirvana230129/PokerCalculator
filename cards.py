from functools import total_ordering


@total_ordering
class Card:
    SUITS = "shdc"
    RANKS = "23456789TJQKA"
    def __init__(self, rank, suit):
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
    """
    Make a deck of 52cards.
    """
    return [Card(rank, suit) for rank in range(13) for suit in range(4)]


def parse_cards(s: str) -> list[Card]:
    """
    Parse a string of cards.
    """
    return [Card(rank, suit) for rank, suit in s.split()]


def cards_to_str(cards: list[Card]) -> str:
    """
    Convert a list of cards to a string.
    """
    return ' '.join(str(card) for card in cards)


def remove_known(deck: list[Card], known: list[Card]) -> list[Card]:
    """
    Remove known cards from a deck (hand or board).
    """
    return [card for card in deck if card not in known]


def group_by_rank(cards: list[Card]) -> dict[int, list[Card]]:
    """
    Group cards by rank.
    """
    ranks_dict: dict[int, list[Card]] = {}
    for card in cards:
        ranks_dict.setdefault(card.rank, []).append(card)
    return ranks_dict


def group_by_suit(cards: list[Card]) -> dict[int, list[Card]]:
    """
    Group cards by suit.
    """
    suits_dict: dict[int, list[Card]] = {}
    for card in cards:
        suits_dict.setdefault(card.suit, []).append(card)
    return suits_dict