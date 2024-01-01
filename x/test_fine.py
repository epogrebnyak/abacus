from copy import deepcopy

import pytest
from fine import (
    Account,
    BalanceSheet,
    Chart,
    ContraIncome,
    Entry,
    IncomeStatement,
    Ledger,
    Pipeline,
    Reporter,
    contra_pairs,
)


def test_ledger_does_not_change_after_copy():
    le0 = (
        Chart(assets=["cash"], capital=["equity"]).ledger().post("cash", "equity", 100)
    )
    assert le0.balances.nonzero() == {"cash": 100, "equity": 100}
    le1 = deepcopy(le0)
    le1 = le1.post("cash", "equity", 200)
    assert le0.balances.nonzero() == {"cash": 100, "equity": 100}


def test_contra_pairs():
    chart = Chart(
        income=[Account("sales", contra_accounts=["refunds", "voids"])],
    )
    assert contra_pairs(chart, ContraIncome) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]


@pytest.fixture
def chart0():
    return Chart(
        assets=["cash"],
        capital=[Account("equity", contra_accounts=["ts"])],
        income=[Account("sales", contra_accounts=["refunds", "voids"])],
        liabilities=["dividend_due"],
        expenses=["salaries"],
    )


@pytest.fixture
def entries0():
    return [
        Entry("cash", "equity", 120),
        Entry("ts", "cash", 20),
        Entry("cash", "sales", 47),
        Entry("refunds", "cash", 5),
        Entry("voids", "cash", 2),
        Entry("salaries", "cash", 30),
    ]


def test_pipleine(chart0, entries0):
    ledger = chart0.ledger().post_many(entries0)
    p = Pipeline(chart0, ledger).close_first().close_second().close_last()
    assert p.ledger.balances.nonzero() == {"cash": 110, "equity": 100, "re": 10}


@pytest.fixture
def reporter0(chart0, entries0):
    ledger = chart0.ledger().post_many(entries0)
    return Reporter(chart0, ledger)


def test_balance_sheet(reporter0):
    assert reporter0.balance_sheet == BalanceSheet(
        assets={"cash": 110},
        capital={"equity": 100, "re": 10},
        liabilities={"dividend_due": 0},
    )


def test_income_statement(reporter0):
    assert reporter0.income_statement == IncomeStatement(
        income={"sales": 40}, expenses={"salaries": 30}
    )


def test_current_account(reporter0):
    assert reporter0.income_statement.current_account() == 10
