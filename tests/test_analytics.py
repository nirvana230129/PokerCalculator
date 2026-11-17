from cards import parse_cards
from analytics import GRID_RANKS, grid_hand_name, hand_grid, hand_grid_from_board, hand_grid_from_preflop, starting_hand_from_cards
from equity import monte_carlo_equity
from precompute import _TABLES, build_preflop_table
from ranges import Range


def test_grid_hand_names_put_pairs_suited_and_offsuit_in_place():
    assert GRID_RANKS[0] == "A"
    assert grid_hand_name(0, 0) == "AA"
    assert grid_hand_name(0, 1) == "AKs"
    assert grid_hand_name(1, 0) == "AKo"
    cards = parse_cards("Ah Kd")
    assert starting_hand_from_cards(cards[0], cards[1]) == "AKo"


def test_monte_carlo_history_ends_at_final_equity():
    result = monte_carlo_equity(parse_cards("As Ah"), [], [Range("KK")], n=40, seed=1)
    assert result.history
    assert result.history[-1] == result.equity
    assert abs(result.win + result.tie + result.lose - 1) < 1e-12


def test_hand_grid_from_preflop_and_board(tmp_path):
    _TABLES.clear()
    build_preflop_table(1, iterations=2, seed=1)
    grid = hand_grid_from_preflop(1)
    assert grid["values"]["AA"] is not None
    assert grid["values"]["AKs"] is not None
    assert grid["values"]["AKo"] is not None

    # One deuce on the board still leaves other 22 combos playable.
    board = parse_cards("2s 7d 9h 4c 3c")
    postflop = hand_grid_from_board(board, [Range("KK")], mode="exact", n=1)
    assert postflop["source"] == "canonical_169"
    assert len(postflop["values"]) == 169
    assert postflop["values"]["AA"] == 1
    assert postflop["values"]["22"] is not None
    assert postflop["values"]["AKs"] is not None

    # Three deuces leave no 22 combo.
    blocked = hand_grid_from_board(parse_cards("2s 2h 2d 7c 9c"), [Range("KK")], mode="exact", n=1)
    assert blocked["values"]["22"] is None
    assert blocked["values"]["AA"] == 1
    _TABLES.clear()


def test_hand_grid_against_range_without_preflop_table():
    _TABLES.clear()
    grid = hand_grid([], opp_ranges=[Range("KK")], mode="monte_carlo", n=20, seed=1)
    assert grid["source"] == "canonical_169"
    assert len(grid["values"]) == 169
    assert grid["values"]["AA"] is not None
    assert grid["values"]["KK"] is not None
