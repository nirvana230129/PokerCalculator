"""Pack a hand's strength into a single integer.

The category and five kickers each occupy 4 bits. The category sits in the high bits,
so comparing the integers compares the hands.
"""

SHIFT_A = 20
SHIFT_B = 16
SHIFT_C = 12
SHIFT_D = 8
SHIFT_E = 4
SHIFT_F = 0

MASK = 0xF  # 4 bits per field

def pack(hand_category: int, kicker1: int = 0, kicker2: int = 0, kicker3: int = 0, kicker4: int = 0, kicker5: int = 0) -> int:
    """Pack a category and up to five kickers into one integer.

    Each argument is truncated to its low 4 bits. An unused kicker stays zero,
    and zero is also the rank of a deuce.
    """
    return (
        ((hand_category & MASK) << SHIFT_A)
        | ((kicker1 & MASK) << SHIFT_B)
        | ((kicker2 & MASK) << SHIFT_C)
        | ((kicker3 & MASK) << SHIFT_D)
        | ((kicker4 & MASK) << SHIFT_E)
        | ((kicker5 & MASK) << SHIFT_F)
    )

def unpack(k: int) -> tuple[int, int, int, int, int, int]:
    """Unpack a ``pack`` integer into the category and five kickers."""
    return (
        (k >> SHIFT_A) & MASK,
        (k >> SHIFT_B) & MASK,
        (k >> SHIFT_C) & MASK,
        (k >> SHIFT_D) & MASK,
        (k >> SHIFT_E) & MASK,
        (k >> SHIFT_F) & MASK,
    )