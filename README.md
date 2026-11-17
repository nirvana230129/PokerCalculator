# Texas Hold'em equity calculator

The program estimates the hero's share of the pot from known hole cards, the cards already on the board, and random or ranged opponent hands.

Equity is the average pot share, not only the rate of outright wins. When the hero splits the pot with one opponent, that trial contributes `1/2`. With more than one opponent, a multiway chop can contribute `1/3`, `1/4`, and so on, so equity is not always `win + tie / 2`.

## What is implemented

| Module | Purpose |
|---|---|
| `cards.py` | A card, parsing strings like `"As Kh"`, and a deck as a list |
| `combo.py` | Packing a hand category and kickers into one integer |
| `evaluator.py` | The best hand from 5, 6, or 7 cards |
| `deck.py` | A deck that deals cards and removes known ones |
| `ranges.py` | Starting hands and range strings |
| `equity.py` | Equity against ranges, by Monte Carlo or exact enumeration |
| `precompute.py` | Saved preflop equity for the 169 canonical hands |
| `parallel.py` | Monte Carlo split across processes |
| `lookup.py` | Precomputed five-card score table |
| `analytics.py` | 13×13 hand-grid helpers for charts |
| `cli.py` | Command-line entry |
| `ui/` | Localhost equity page |
| `tests/` | Pytest checks for these modules |

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

`result.exact` is `False`: this is a sample, so another run without the same `seed` gives a slightly different number. `win`, `tie`, and `lose` are trial shares and add up to 1. Unknown opponents are dealt from the remaining deck, which is much faster than sampling through a full range of every starting hand.

### Command line

```bash
python cli.py --hero "As Kh" --board "Qd 7c 2s" --villain "JJ+, AKs"
python cli.py --hero "As Kh" --opponents 3 --samples 100000
python cli.py --board "Qd 7c 2s" --all-hands
```

Useful flags: `--mode auto|exact|monte_carlo`, `--samples`, `--seed`, `--workers`. `--villain` and `--opponents` cannot be combined. `--all-hands` does not take `--hero`.

### Local page

```bash
python cli.py --ui
```

Opens `http://127.0.0.1:8765/`. Pick hero and board cards with the rank and suit buttons, then choose opponents:

- **Unknown hands (random)** — use this when you do not know their cards. Set how many opponents sit at the table (1–8). Each is dealt a random hole hand from the remaining deck.
- **Known range** — use a range string such as `JJ+, AKs` when you have a read.

`Mode` and `Samples` control the calculation. `auto` uses exact enumeration when the tree is small, otherwise Monte Carlo. Long requests show a live elapsed timer.

After **Calculate**:

- the result line shows equity, win / tie / lose, samples, method, and elapsed time;
- **Win / tie / lose** is the share of trials in each outcome;
- **Monte Carlo convergence** is the running equity estimate as more deals are sampled. A flat line means the estimate has settled; the label on the right is the final equity.

**Show 13×13 grid** fills the classic starting-hand matrix against the same opponents and board. Each cell is equity in percent (for example `45` means about 45% pot share). The diagonal is pairs, the upper triangle is suited, the lower triangle is offsuit. An empty cell means every combo of that hand is blocked by the board. The grid evaluates 169 canonical hands and caps Monte Carlo samples per cell so it stays interactive.

The first equity call builds `data/five_card_ranks.bin` if it is missing. That file is not committed.

### Tests

Run the checks from the project root:

```bash
python -m pytest
```
