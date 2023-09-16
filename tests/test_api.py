import pytest  # type: ignore

from abacus.api import Chart, ChartCommand
from abacus.engine.accounts import ContraIncome


@pytest.fixture
def chart():
    return ChartCommand(Chart())


def test_add_assets(chart):
    chart.add_asset("cash")
    assert chart.chart.assets == ["cash"]


def test_add_capital(chart):
    chart.add_capital("equity")
    assert chart.chart.equity == ["equity"]


def test_add_liabilities(chart):
    chart.add_liability("ap")
    assert chart.chart.liabilities == ["ap"]


def test_add_income(chart):
    chart.add_income("sales")
    assert chart.chart.income == ["sales"]


def test_add_expenses(chart):
    chart.add_expense("cogs")
    assert chart.chart.expenses == ["cogs"]


def test_add_on_nonexistent_attribute():
    with pytest.raises(AttributeError):
        ChartCommand(chart=Chart())._add("no such attribute", [])


def test_split_on_caps():
    assert ContraIncome([], []).split_on_caps() == "Contra Income"
