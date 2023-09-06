import pytest
from api import AbacusError, Chart, ChartCommand

# TODO: create test_api.py and code with asserts to test_api.py as pytest unit tests
#      use nsames like test_add_tests(),
#      the following command should run as a test: poetry run pytest experimental
#      if you install just command runner `just go` should also pass


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
    with pytest.raises(AbacusError):
        ChartCommand(Chart())._add("no such attribute", [])
