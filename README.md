# Texas Hold'em equity calculator

The program estimates the hero's share of the pot from known hole cards, the cards already on the board, and random opponent hands.

Equity is the average pot share, not only the rate of outright wins. When the hero splits the pot with one opponent, that trial contributes `1/2`.

## What is implemented

| Module | Purpose |
|---|---|
| `cards.py` | A card, parsing strings like `"As Kh"`, and a deck as a list |
| `combo.py` | Packing a hand category and kickers into one integer |
| `evaluator.py` | The best hand from 5, 6, or 7 cards |
| `deck.py` | A deck that deals cards and removes known ones |
| `equity.py` | Monte Carlo equity against random opponents |
| `tests/` | Pytest checks for these modules |

The remaining work is described in `plan.md`. Hand ranges, exact board enumeration, and preflop tables are not implemented yet.

## Running

Python 3.11+ and `tqdm` (used for the Monte Carlo progress bar):

```bash
pip install tqdm
```

Aces versus one random opponent before the flop. Over 100,000 trials the pot share is about `0.85`.

```python
from cards import parse_cards
from equity import equity_vs_random

result = equity_vs_random(parse_cards("As Ah"), [], n_opponents=1, n=100_000, seed=1)
print(result.equity, result.win, result.tie, result.lose)
```

`result.exact` is `False`: this is a sample, so another run without the same `seed` gives a slightly different number. `win`, `tie`, and `lose` are trial shares and add up to 1.

Run the checks from the project root:

```bash
python -m pytest
```
