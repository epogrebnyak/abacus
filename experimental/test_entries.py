# This is pytest unit test file for experimental/entries.py

import pytest  # type: ignore
from engine.base import Entry
from experimental.engine.entries import CsvFile


@pytest.fixture
def path(tmp_path):
    return tmp_path / "entries.csv"


def test_yield_entries(path):
    file = CsvFile(path)
    file.touch()
    e1, e2 = Entry("cash", "equity", 499), Entry("cash", "equity", 501)
    file.append(e1)
    file.append(e2)
    assert list(file.yield_entries()) == [e1, e2]
