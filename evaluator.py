from cards import *
from combo import pack, unpack
from enum import IntEnum
from itertools import combinations


class HandCategory(IntEnum):
    HIGH_CARD = 0
    PAIR = 1
    TWO_PAIR = 2
    THREE_OF_A_KIND = 3
    STRAIGHT = 4
    FLUSH = 5
    FULL_HOUSE = 6
    FOUR_OF_A_KIND = 7
    STRAIGHT_FLUSH = 8
    ROYAL_FLUSH = 9

HAND_NAMES = {
    HandCategory.HIGH_CARD: "High Card",
    HandCategory.PAIR: "Pair",
    HandCategory.TWO_PAIR: "Two Pair",
    HandCategory.THREE_OF_A_KIND: "Three of a Kind",
    HandCategory.STRAIGHT: "Straight",
    HandCategory.FLUSH: "Flush",
    HandCategory.FULL_HOUSE: "Full House",
    HandCategory.FOUR_OF_A_KIND: "Four of a Kind",
    HandCategory.STRAIGHT_FLUSH: "Straight Flush",
    HandCategory.ROYAL_FLUSH: "Royal Flush",
}


WHEEL_RANKS = [0, 1, 2, 3, 12]

def evaluate_5(cards: list[Card]) -> int:
    if len(cards) != 5:
        raise ValueError(f"Invalid number of cards: it must be 5, not {len(cards)}")

    ranks = sorted([card.rank for card in cards])

    is_flush = len({card.suit for card in cards}) == 1
    is_straight = False
    is_wheel = False
    if len(set(ranks)) == 5:
        is_wheel = ranks == WHEEL_RANKS
        is_straight = is_wheel or ranks[-1] - ranks[0] == 4

    ranks_dict: dict[int, int] = {}
    for card in cards:
        ranks_dict[card.rank] = ranks_dict.get(card.rank, 0) + 1

    by_count: dict[int, list[int]] = {}
    for rank, count in ranks_dict.items():
        by_count.setdefault(count, []).append(rank)
    for group in by_count.values():
        group.sort(reverse=True)

    if is_straight and is_flush:
        if ranks[0] == 8:
            return pack(HandCategory.ROYAL_FLUSH)                                       # 9 - Flash royal
        return pack(HandCategory.STRAIGHT_FLUSH, ranks[-2] if is_wheel else ranks[-1])  # 8 - Straight flush
    if len(ranks_dict) == 2:
        if 4 in by_count:
            return pack(HandCategory.FOUR_OF_A_KIND, *by_count[4], *by_count[1])        # 7 - Four of a kind
        return pack(HandCategory.FULL_HOUSE, *by_count[3], *by_count[2])                # 6 - Full house
    if is_flush:
        flush_ranks = reversed(ranks)
        return pack(HandCategory.FLUSH, *flush_ranks)                                   # 5 - Flush
    if is_straight:
        return pack(HandCategory.STRAIGHT, ranks[-2] if is_wheel else ranks[-1])        # 4 - Straight
    if len(ranks_dict) == 3:
        if 3 in by_count:
            return pack(HandCategory.THREE_OF_A_KIND, *by_count[3], *by_count[1])       # 3 - Three of a kind
        return pack(HandCategory.TWO_PAIR, *by_count[2], *by_count[1])                  # 2 - Two pairs
    if len(ranks_dict) == 4:
        return pack(HandCategory.PAIR, *by_count[2], *by_count[1])                      # 1 - One pair
    return pack(HandCategory.HIGH_CARD, *by_count[1])                                   # 0 - High card


def evaluate(cards: list[Card]) -> int:
    if len(cards) < 5:
        raise ValueError(f"For a standard poker hand, you need at least 5 cards, not {len(cards)}")    
    return max(evaluate_5(combo) for combo in combinations(cards, 5))


def hand_category(score: int) -> HandCategory:
    return HandCategory(unpack(score)[0])

def describe_hand(score: int) -> str:
    return f"{hand_category(score)}: {', '.join(str(rank) for rank in unpack(score)[1:])}"

def compare(a: int, b: int) -> int:
    return (a > b) - (a < b)
