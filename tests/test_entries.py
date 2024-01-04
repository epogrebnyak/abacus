from pathlib import Path

import pytest

from abacus.core import Chart, Entry
from abacus.entries_store import LineJSON


@pytest.fixture
def path(tmp_path):
    return Path(tmp_path) / "entries.csv"


def test_yield_entries(path):
    path.touch()
    store = LineJSON(path)
    e1, e2 = Entry("cash", "equity", 499), Entry("cash", "equity", 501)
    store.append_many([e1, e2])
    assert list(store.yield_entries()) == [e1, e2]


def test_yield_entries_for_income_statement(path):
    path.touch()
    store = LineJSON(path)
    e1 = Entry("cash", "equity", 10)
    e2 = Entry("sales", "isa", 5)
    store.append(e1)
    store.append(e2)
    chart = Chart("isa", "re", "null")
    assert list(store.yield_entries_for_income_statement(chart)) == [e1]
