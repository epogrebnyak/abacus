from engine.accounts import (
    Asset,
    Capital,
    ContraIncome,
    Expense,
    IncomeSummaryAccount,
    NullAccount,
    RetainedEarnings,
)
from engine.base import Entry, MultipleEntry
from engine.chart import Chart
from engine.ledger import Ledger, to_multiple_entry


def test_ledger(ledger):
    assert {
        k: v
        for k, v in ledger.subset([Asset, Expense, ContraIncome])
        .deep_copy()
        .condense()
        .balances()
        .items()
        if v
    } == {"cash": 1000, "ar": 200, "refunds": 50}


def test_ledger_new():
    assert Ledger.new(Chart(assets=["cash"], equity=["equity"])).data == {
        "cash": Asset(debits=[], credits=[]),
        "equity": Capital(debits=[], credits=[]),
        "re": RetainedEarnings(debits=[], credits=[]),
        "current_profit": IncomeSummaryAccount(debits=[], credits=[]),
        "null": NullAccount(debits=[], credits=[]),
    }


def test_ledger_post():
    ledger1 = Ledger.new(Chart(assets=["cash"], equity=["equity"]))
    ledger1.post(Entry(debit="cash", credit="equity", amount=799))
    ledger1.post(Entry(debit="cash", credit="equity", amount=201))
    assert ledger1["cash"].debits == ledger1["equity"].credits == [799, 201]
    assert ledger1["cash"].balance() == ledger1["equity"].balance() == 1000


def test_ledger_deep_copy():
    ledger1 = Ledger.new(Chart(assets=["cash"], equity=["equity"]))
    ledger1.post(Entry(debit="cash", credit="equity", amount=799))
    ledger1.post(Entry(debit="cash", credit="equity", amount=201))
    ledger2 = ledger1.deep_copy()
    ledger2.post(Entry(debit="cash", credit="equity", amount=-1000))
    # ledger1 not affected
    assert ledger1["cash"].balance() == ledger1["equity"].balance() == 1000
    # ledger2 changed
    assert ledger2["cash"].balance() == ledger2["equity"].balance() == 0


def test_ledger_report_balance_sheet(chart, ledger):
    assert ledger.balance_sheet(chart).dict() == {
        "assets": {"cash": 1000, "ar": 200, "goods": 0},
        "capital": {"equity": 1000, "re": 200},
        "liabilities": {},
    }


def test_ledger_report_income_statement(chart, ledger):
    assert ledger.income_statement(chart).dict() == {
        "income": {"sales": 200},
        "expenses": {"cogs": 0, "sga": 0},
    }


def test_journal_with_starting_balance():
    chart = Chart(
        assets=["cash"],
        equity=["equity"],
        expenses=["salaries", "rent"],
        liabilities=[],
        income=["services"],
    )
    ledger = Ledger.new(chart)

    # Account balances are known from previous period end
    starting_balances = {"cash": 1400, "equity": 1500, "re": -100}
    assert to_multiple_entry(ledger, starting_balances) == MultipleEntry(
        [("cash", 1400)],
        [("equity", 1500), ("re", -100)],
    )
