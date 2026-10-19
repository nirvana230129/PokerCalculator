from cards import Card, cards_to_str
import random
from typing import Iterator

class Deck:
    CARDS = [Card(rank, suit) for rank in range(13) for suit in range(4)]
    def __init__(self, shuffle: bool = True):
        self.remake(shuffle)
    
    def remake(self, shuffle: bool = True) -> None:
        self.positions = list(range(len(self.CARDS)))
        if shuffle:
            random.shuffle(self.positions)
    
    def draw(self, n: int = 1) -> list[Card]:
        if n < 0 or n > len(self.positions):
            raise ValueError(f"Cannot draw {n} cards from a deck of {len(self.positions)} cards")
        to_draw = self.__getitem__(slice(0, n))
        self.positions = self.positions[n:]
        return to_draw

    def remove(self, cards: list[Card]) -> None:
        self.positions = [i for i in self.positions if self.CARDS[i] not in cards]
    
    def remaining(self) -> list[Card]:
        return self.__getitem__(slice(0, len(self.positions)))
    
    def __getitem__(self, index: int | slice) -> Card | list[Card]:
        if isinstance(index, slice):
            return [self.CARDS[i] for i in self.positions[index]]
        return self.CARDS[self.positions[index]]

    def __iter__(self) -> Iterator[Card]:
        return iter(self.CARDS[i] for i in self.positions)
    
    def __len__(self) -> int:
        return len(self.positions)
    
    def __str__(self) -> str:
        return cards_to_str(self.remaining())
    
    def __repr__(self) -> str:
        return f"Deck({len(self.positions)} cards)"
