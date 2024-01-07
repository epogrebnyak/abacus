import pytest
from abacus.core import AccountBalances as AB
from abacus.core import BalanceSheet
from abacus.core import IncomeStatement
from abacus.viewers import BalanceSheetViewer, IncomeStatementViewer, TrialBalanceViewer


@pytest.fixture
def balance_sheet_viewer():
    b = BalanceSheet(
        assets=AB(cash=200),
        capital=AB(equity=150, retained_earnings=-20),
        liabilities=AB(loan=65, dd=5),
    )
    return BalanceSheetViewer(
        b,
        rename_dict=dict(
            assets="активы", cash="касса", dd="dividend due", total="итого"
        ),
        title="Баланс",
    )


@pytest.mark.unit
def test_balance_sheet_viewer_width(balance_sheet_viewer):
    assert balance_sheet_viewer.width == 38


@pytest.mark.unit
def test_balance_sheet_deep_rename(balance_sheet_viewer):
    assert "ИТОГО" in str(balance_sheet_viewer)


@pytest.mark.callable
def test_balance_sheet_viewer(balance_sheet_viewer):
    balance_sheet_viewer.print()
    balance_sheet_viewer.print(80)


@pytest.fixture
def income_statement_viewer():
    i = IncomeStatement(income=AB(sales=40), expenses=AB(rent=25, salaries=35))
    return IncomeStatementViewer(i, "My! income statement")


@pytest.mark.callable
def test_viewer_is(income_statement_viewer):
    assert "My! income statement" in str(income_statement_viewer)
    income_statement_viewer.print()
    income_statement_viewer.print(80)


@pytest.mark.callable
def test_trial_balance_viewer():
    vtb = TrialBalanceViewer(dict(cash=(100, 0), equity=(0, 120), re=(0, -20)))
    assert "cash" in str(vtb)
    vtb.print()
    vtb.print(80)
