SHIFT_A = 20
SHIFT_B = 16
SHIFT_C = 12
SHIFT_D = 8
SHIFT_E = 4
SHIFT_F = 0

MASK = 0xF  # 4 bits per field

def pack(hand_category: int, kicker1: int = 0, kicker2: int = 0, kicker3: int = 0, kicker4: int = 0, kicker5: int = 0) -> int:
    return (
        ((hand_category & MASK) << SHIFT_A)
        | ((kicker1 & MASK) << SHIFT_B)
        | ((kicker2 & MASK) << SHIFT_C)
        | ((kicker3 & MASK) << SHIFT_D)
        | ((kicker4 & MASK) << SHIFT_E)
        | ((kicker5 & MASK) << SHIFT_F)
    )

def unpack(k: int) -> tuple[int, int, int, int, int, int]:
    return (
        (k >> SHIFT_A) & MASK,
        (k >> SHIFT_B) & MASK,
        (k >> SHIFT_C) & MASK,
        (k >> SHIFT_D) & MASK,
        (k >> SHIFT_E) & MASK,
        (k >> SHIFT_F) & MASK,
    )