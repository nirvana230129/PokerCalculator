"""Canonical starting hands and ranges built from them.

A starting hand such as ``AKs`` or ``QQ`` stands for every concrete pair of cards
of that kind. A range is a set of those hands. ``+`` and ``-`` keep the hand shape
fixed: a pair walks its rank, and a non-pair walks only its second rank.
"""

from cards import Card


class StartingHand:
    """One hand type: a pair, two suited cards, or two offsuit cards.

    The higher rank is stored first. Pairs have no suitedness. ``"AK"`` without
    ``s`` or ``o`` is rejected, because it does not say whether the cards share a suit.
    """

    def __init__(self, s: str):
        """Parse ``s`` and store the hand. See ``from_str``."""
        self.from_str(s)

    def from_str(self, s: str) -> None:
        """Read ``"QQ"``, ``"AKs"``, or ``"AKo"``.

        Ranks written out of order are swapped, so ``"KAs"`` becomes ``AKs``.

        Raises:
            ValueError: the text is not one of those three forms.
        """
        text = s.strip()
        suited = None
        body = text
        if len(text) == 3 and text[2].lower() in "so":
            body = text[:2]
            suited = text[2].lower() == "s"
        if len(body) != 2:
            raise ValueError(f"Invalid starting hand: {s}")

        rank1, rank2 = body[0:2].upper()
        if rank1 not in Card.RANKS or rank2 not in Card.RANKS:
            raise ValueError(f"Invalid rank: {rank1} {rank2}")
        if Card.RANKS.index(rank1) < Card.RANKS.index(rank2):
            rank1, rank2 = rank2, rank1
        self.rank1 = rank1
        self.rank2 = rank2
        if rank1 == rank2:
            self.suited = None
        elif suited is None:
            raise ValueError(f"Non-pair hand needs s or o: {s}")
        else:
            self.suited = suited

    def __str__(self) -> str:
        if self.rank1 == self.rank2:
            return f"{self.rank1}{self.rank2}"
        return f"{self.rank1}{self.rank2}{'s' if self.suited else 'o'}"

    def __eq__(self, other: object) -> bool:
        return isinstance(other, StartingHand) and str(self) == str(other)

    def __hash__(self) -> int:
        return hash(str(self))

    def to_combos(self) -> list[list[Card]]:
        """Expand the hand into concrete two-card combinations.

        A pair has 6, a suited hand has 4, and an offsuit hand has 12.
        """
        suits = Card.SUITS
        if self.rank1 == self.rank2:
            return [
                [Card(self.rank1, suits[i]), Card(self.rank1, suits[j])]
                for i in range(len(suits))
                for j in range(i + 1, len(suits))
            ]
        if self.suited:
            return [[Card(self.rank1, suit), Card(self.rank2, suit)] for suit in suits]
        return [
            [Card(self.rank1, suit1), Card(self.rank2, suit2)]
            for suit1 in suits
            for suit2 in suits
            if suit1 != suit2
        ]


class Range:
    """A set of starting hands, parsed from a range string.

    ``"22+"`` is every pair from deuces to aces. ``"A2s+"`` is suited aces from
    ``A2s`` through ``AKs``: the ace and the suitedness stay, and the second rank
    moves up. ``"JJ-99"`` and ``"AQs-ATs"`` are the inclusive span between the two
    bounds. Every hand has weight 1; weights are not used yet.
    """

    def __init__(self, s: str):
        """Parse ``s`` into ``self.hands``. See ``from_str``."""
        self.weight = 1
        self.hands: list[StartingHand] = []
        self.from_str(s)

    def from_str(self, s: str) -> None:
        """Replace ``self.hands`` with the hands described by ``s``.

        Tokens are separated by commas. Each token is one hand, a ``+`` tail, or a
        ``-`` span.

        Raises:
            ValueError: a token is not a hand, or the two sides of ``-`` do not share a shape.
        """
        self.hands = []
        seen: set[StartingHand] = set()
        for token in s.split(","):
            for hand in self._expand(token.strip()):
                if hand not in seen:
                    seen.add(hand)
                    self.hands.append(hand)

    def _expand(self, token: str) -> list[StartingHand]:
        if token.endswith("+"):
            return self._expand_plus(StartingHand(token[:-1]))
        if "-" in token:
            left, right = token.split("-")
            return self._expand_minus(StartingHand(left), StartingHand(right))
        return [StartingHand(token)]

    def _expand_plus(self, hand: StartingHand) -> list[StartingHand]:
        start = Card.RANKS.index(hand.rank2)
        stop = Card.RANKS.index(hand.rank1)
        if hand.rank1 == hand.rank2:
            return [StartingHand(Card.RANKS[i] * 2) for i in range(start, len(Card.RANKS))]
        suffix = "s" if hand.suited else "o"
        return [
            StartingHand(f"{hand.rank1}{Card.RANKS[i]}{suffix}")
            for i in range(start, stop)
        ]

    def _expand_minus(self, left: StartingHand, right: StartingHand) -> list[StartingHand]:
        if (left.rank1 == left.rank2) != (right.rank1 == right.rank2):
            raise ValueError(f"Range bounds have different shapes: {left} and {right}")
        if left.rank1 == left.rank2:
            low = min(Card.RANKS.index(left.rank1), Card.RANKS.index(right.rank1))
            high = max(Card.RANKS.index(left.rank1), Card.RANKS.index(right.rank1))
            return [StartingHand(Card.RANKS[i] * 2) for i in range(low, high + 1)]
        if left.rank1 != right.rank1 or left.suited != right.suited:
            raise ValueError(f"Range bounds have different shapes: {left} and {right}")
        low = min(Card.RANKS.index(left.rank2), Card.RANKS.index(right.rank2))
        high = max(Card.RANKS.index(left.rank2), Card.RANKS.index(right.rank2))
        suffix = "s" if left.suited else "o"
        return [
            StartingHand(f"{left.rank1}{Card.RANKS[i]}{suffix}")
            for i in range(low, high + 1)
        ]

    def uniform(self) -> None:
        """Replace the range with all 169 starting hands, the random-opponent range."""
        self.hands = []
        for i, rank1 in enumerate(Card.RANKS):
            self.hands.append(StartingHand(rank1 * 2))
            for rank2 in Card.RANKS[i + 1:]:
                self.hands.append(StartingHand(f"{rank2}{rank1}s"))
                self.hands.append(StartingHand(f"{rank2}{rank1}o"))

    def combos(self, blockers: list[Card] | None = None) -> list[list[Card]]:
        """Concrete two-card combinations that do not use a card in ``blockers``.

        Blockers are cards already dealt: the hero's hand, the board, or another
        opponent's hand. A combination that contains any of them is left out.
        """
        blocked = set(blockers or [])
        result = []
        for hand in self.hands:
            for combo in hand.to_combos():
                if not any(card in blocked for card in combo):
                    result.append(combo)
        return result

    def size(self, blockers: list[Card] | None = None) -> int:
        """Number of concrete combinations, after removing ``blockers``."""
        return len(self.combos(blockers))

    def __str__(self) -> str:
        return " ".join(str(hand) for hand in self.hands)

    def __len__(self) -> int:
        """Number of starting-hand types, not concrete combinations."""
        return len(self.hands)

    def __iter__(self):
        return iter(self.hands)
