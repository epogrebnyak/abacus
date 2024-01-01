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
    Asset,
    Capital,
    AbacusError,
)


@pytest.mark.regression
def test_ledger_does_not_change_after_copy():
    le0 = (
        Chart(assets=["cash"], capital=["equity"]).ledger().post("cash", "equity", 100)
    )
    assert le0.balances.nonzero() == {"cash": 100, "equity": 100}
    le1 = deepcopy(le0)
    le1 = le1.post("cash", "equity", 200)
    assert le0.balances.nonzero() == {"cash": 100, "equity": 100}


@pytest.mark.unit
def test_contra_pairs():
    chart = Chart(
        income=[Account("sales", contra_accounts=["refunds", "voids"])],
    )
    assert contra_pairs(chart, ContraIncome) == [
        ("sales", "refunds"),
        ("sales", "voids"),
    ]


@pytest.mark.unit
def test_ledger():
    ledger = Ledger({"cash": Asset(), "equity": Capital()}).post("cash", "equity", 1000)
    assert ledger == Ledger({"cash": Asset([1000], []), "equity": Capital([], [1000])})


@pytest.mark.unit
def test_ledger_condense():
    Ledger({"cash": Asset([300, 100], [200])}).condense() == Ledger(
        {"cash": Asset([200], [])}
    )

@pytest.mark.unit
def test_ledger_fails_on_unknown_account_name():
    with pytest.raises(AbacusError):
        Ledger({"cash": Asset(), "equity": Capital()}).post("cash", "xxx", 1000)


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

@pytest.mark.e2e
def test_pipleine(chart0, entries0):
    ledger = chart0.ledger().post_many(entries0)
    p = Pipeline(chart0, ledger).close_first().close_second().close_last()
    assert p.ledger.balances.nonzero() == {"cash": 110, "equity": 100, "re": 10}


@pytest.fixture
def reporter0(chart0, entries0):
    ledger = chart0.ledger().post_many(entries0)
    return Reporter(chart0, ledger)


@pytest.mark.e2e
def test_balance_sheet(reporter0):
    assert reporter0.balance_sheet == BalanceSheet(
        assets={"cash": 110},
        capital={"equity": 100, "re": 10},
        liabilities={"dividend_due": 0},
    )


@pytest.mark.e2e
def test_income_statement(reporter0):
    assert reporter0.income_statement == IncomeStatement(
        income={"sales": 40}, expenses={"salaries": 30}
    )


@pytest.mark.e2e
def test_current_account(reporter0):
    assert reporter0.income_statement.current_account() == 10


@pytest.mark.e2e
def test_trial_balance(reporter0):
    assert reporter0.trial_balance.data == {
        "cash": (110, 0),
        "ts": (20, 0),
        "refunds": (5, 0),
        "voids": (2, 0),
        "salaries": (30, 0),
        "equity": (0, 120),
        "re": (0, 0),
        "dividend_due": (0, 0),
        "sales": (0, 47),
        "isa": (0, 0),
        "null": (0, 0),
    }
