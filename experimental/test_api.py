import pytest  # type: ignore
from api import Chart, ChartCommand


def test_add_assets():
    assert ChartCommand(Chart()).add_assets(["cash"]).chart.assets == ["cash"]


def test_add_capital():
    assert ChartCommand(Chart()).add_capital(["equity"]).chart.equity == ["equity"]


def test_add_liabilities():
    assert ChartCommand(Chart()).add_liabilities(["ap"]).chart.liabilities == ["ap"]


def test_add_income():
    assert ChartCommand(Chart()).add_income(["sales"]).chart.income == ["sales"]


def test_add_expenses():
    assert ChartCommand(Chart()).add_expenses(["cogs"]).chart.expenses == ["cogs"]


def test_add_on_nonexistent_attribute():
    with pytest.raises(AttributeError):
        ChartCommand(chart=Chart())._add("no such attribute", [])


def test_split_on_caps():
    from api import split_on_caps
    from engine.accounts import ContraIncome

    assert split_on_caps(ContraIncome([], [])) == "Contra Income"
