import pytest  # pylint: disable=import-error

from abacus.accounting_types import (
    Asset,
    BalanceSheet,
    Capital,
    IncomeStatement,
    IncomeSummaryAccount,
)
from abacus.core import Chart, Entry, Ledger, make_ledger, safe_process_entries


@pytest.fixture
def chart():
    return Chart(
        assets=["cash", "receivables", "goods_for_sale"],
        expenses=["cogs", "sga"],
        equity=["equity", "re"],
        liabilities=["divp", "payables"],
        income=["sales"],
    )


@pytest.fixture
def entries():
    e1 = Entry(dr="cash", cr="equity", amount=1000)
    e2 = Entry(dr="goods_for_sale", cr="cash", amount=250)
    e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200)
    e4 = Entry(cr="sales", dr="cash", amount=400)
    e5 = Entry(cr="cash", dr="sga", amount=50)
    return [e1, e2, e3, e4, e5]


def test_make_ledger():
    _chart = Chart(
        assets=["cash"], equity=["equity"], income=[], expenses=[], liabilities=[]
    )
    assert make_ledger(_chart) == {
        "cash": Asset(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "profit": IncomeSummaryAccount(debits=[], credits=[]),
    }


def test_safe_process_entries():
    _ledger = Ledger(
        {
            "cash": Asset(debits=[], credits=[]),
            "equity": Capital(debits=[], credits=[]),
            "profit": IncomeSummaryAccount(debits=[], credits=[]),
        }
    )
    _, _failed = safe_process_entries(_ledger, [Entry("", "", 0)])
    assert _failed == [Entry("", "", 0)]


def test_income_statement(chart, entries):
    income_st = chart.make_ledger().process_entries(entries).income_statement()
    assert income_st == IncomeStatement(
        income={"sales": 400}, expenses={"cogs": 200, "sga": 50}
    )


def test_balance_sheet_with_close(chart, entries):
    balance_st = (
        chart.make_ledger().process_entries(entries).close_retained_earnings("re").balance_sheet()
    )
    assert balance_st == BalanceSheet(
        assets={"cash": 1100, "receivables": 0, "goods_for_sale": 50},
        capital={"equity": 1000, "re": 150},
        liabilities={"divp": 0, "payables": 0},
    )


def test_balances(chart, entries):
    b = chart.make_ledger().process_entries(entries).close_retained_earnings("re").balances()
    assert b == {
        "cash": 1100,
        "receivables": 0,
        "goods_for_sale": 50,
        "cogs": 0,
        "sga": 0,
        "equity": 1000,
        "re": 150,
        "divp": 0,
        "payables": 0,
        "sales": 0,
        "profit": 0,
    }
