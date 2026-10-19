"""Карта и операции над списками карт.

Ранг — число 0..12 в порядке ``23456789TJQKA``. Масть — число 0..3 в порядке ``shdc``.
"""

from functools import total_ordering


@total_ordering
class Card:
    """Одна карта колоды.

    Создаётся парой чисел ``Card(12, 0)`` или парой символов ``Card("A", "s")``.
    ``int(card)`` — номер 0..51, равный ``rank * 4 + suit``. Равные карты сравниваются
    и хешируются по этому номеру, поэтому их можно класть в ``set``.
    """

    SUITS = "shdc"
    RANKS = "23456789TJQKA"

    def __init__(self, rank, suit):
        """Принять ранг и масть числами или символами.

        Raises:
            ValueError: ранг или масть вне колоды.
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
    """Вернуть новую колоду из 52 карт, от ``2s`` до ``Ac``."""
    return [Card(rank, suit) for rank in range(13) for suit in range(4)]


def parse_cards(s: str) -> list[Card]:
    """Разобрать строку карт, разделённых пробелами.

    ``"As Kh Qd"`` даёт три карты. Слитная запись ``"AsKh"`` не разбирается.
    """
    return [Card(rank, suit) for rank, suit in s.split()]


def cards_to_str(cards: list[Card]) -> str:
    """Собрать карты обратно в строку вида ``"As Kh Qd"``."""
    return ' '.join(str(card) for card in cards)


def remove_known(deck: list[Card], known: list[Card]) -> list[Card]:
    """Вернуть копию колоды без карт из ``known``. Исходный список не меняется."""
    return [card for card in deck if card not in known]


def group_by_rank(cards: list[Card]) -> dict[int, list[Card]]:
    """Сгруппировать карты по рангу. Ключ — число 0..12."""
    ranks_dict: dict[int, list[Card]] = {}
    for card in cards:
        ranks_dict.setdefault(card.rank, []).append(card)
    return ranks_dict


def group_by_suit(cards: list[Card]) -> dict[int, list[Card]]:
    """Сгруппировать карты по масти. Ключ — число 0..3 в порядке ``shdc``."""
    suits_dict: dict[int, list[Card]] = {}
    for card in cards:
        suits_dict.setdefault(card.suit, []).append(card)
    return suits_dict