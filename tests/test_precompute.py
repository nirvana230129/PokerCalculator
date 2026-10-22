import pytest

from precompute import _TABLES, build_preflop_table, load_table, lookup_preflop, save_table


@pytest.fixture(autouse=True)
def clear_tables():
    _TABLES.clear()
    yield
    _TABLES.clear()


def test_lookup_returns_the_saved_value_without_simulating_again(tmp_path, monkeypatch):
    table = build_preflop_table(1, iterations=2, seed=1)
    assert len(table) == 169
    assert table["AA"].samples == 2

    path = tmp_path / "preflop.json"
    save_table(path, 1)
    _TABLES.clear()

    def fail_if_simulated(*args, **kwargs):
        raise AssertionError("simulated again")

    monkeypatch.setattr("precompute.equity_vs_random", fail_if_simulated)
    load_table(path)
    loaded = lookup_preflop("aa", 1)
    assert loaded.equity == table["AA"].equity
    assert loaded.samples == 2
    assert lookup_preflop("AKs", 1).samples == 2


def test_lookup_requires_a_built_table():
    with pytest.raises(KeyError):
        lookup_preflop("AA", 1)
    with pytest.raises(ValueError):
        build_preflop_table(1, iterations=0)
    with pytest.raises(KeyError):
        save_table("unused.json", 1)
