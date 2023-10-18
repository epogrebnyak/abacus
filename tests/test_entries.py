from pathlib import Path

import pytest  # type: ignore

from abacus import Chart
from abacus.engine.base import Entry
from abacus.engine.entries import LineJSON


@pytest.fixture
def path(tmp_path):
    return Path(tmp_path) / "entries.csv"


def test_yield_entries(path):
    store = LineJSON(path)
    store.file.touch()
    e1, e2 = Entry("cash", "equity", 499), Entry("cash", "equity", 501)
    store.append_many([e1, e2])
    assert list(store.yield_entries()) == [e1, e2]


def test_yield_entries_for_income_statement(path):
    store = LineJSON(path)
    store.file.erase().touch()
    e1 = Entry("cash", "equity", 100)
    e2 = Entry("sales", "isa", 5)
    store.append(e1)
    store.append(e2)
    chart = Chart()
    chart.income_summary_account = "isa"
    assert list(store.yield_entries()) == [e1, e2]
    assert list(store.yield_entries_for_income_statement(chart)) == [e1]
