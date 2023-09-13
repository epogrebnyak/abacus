from engine.chart import Chart
from engine.base import Entry
from engine.report import BalanceSheet, IncomeStatement


# Create chart of accounts
chart = Chart(
    assets=["cash"],
    equity=["equity"],
    expenses=["salaries", "rent"],
    liabilities=[],
    income=["services"],
).offset("services", ["cashback"])


# Account balances are known from previous period end
starting_balances = {"cash": 1400, "equity": 1500, "re": -100}

# Create general ledger and post new entries
ledger = (
    chart.ledger(starting_balances)
    .post(Entry(debit="rent", credit="cash", amount=200))
    .post(Entry(debit="cash", credit="services", amount=825))
    .post(Entry(debit="cashback", credit="cash", amount=25))
    .post(Entry(debit="salaries", credit="cash", amount=400))
)

from engine.closing import make_closing_entries, ClosingEntries


def test_closing_entries():
    assert make_closing_entries(chart, ledger) == ClosingEntries(
        closing_contra_income=[Entry(debit="services", credit="cashback", amount=25)],
        closing_contra_expense=[],
        closing_income=[Entry(debit="services", credit="current_profit", amount=800)],
        closing_expense=[
            Entry(debit="current_profit", credit="salaries", amount=400),
            Entry(debit="current_profit", credit="rent", amount=200),
        ],
        closing_isa=Entry(debit="current_profit", credit="re", amount=200),
    )


def test_closing_entries_for_is():
    assert ledger.closing_entries_for_income_statement(chart) == [
        Entry(debit="services", credit="cashback", amount=25)
    ]


def test_closing_entries_for_bs():
    assert ledger.closing_entries_for_balance_sheet(chart) == [
        Entry(debit="services", credit="cashback", amount=25),
        Entry(debit="services", credit="current_profit", amount=800),
        Entry(debit="current_profit", credit="salaries", amount=400),
        Entry(debit="current_profit", credit="rent", amount=200),
        Entry(debit="current_profit", credit="re", amount=200),
    ]


def test_balance_sheet():
    assert ledger.balance_sheet(chart) == BalanceSheet(
        assets={"cash": 1600}, capital={"equity": 1500, "re": 100}, liabilities={}
    )


def test_balances():
    assert ledger.condense().close(chart).balances() == {
        "current_profit": 0,
        "null": 0,
        "cashback": 0,
        "cash": 1600,
        "equity": 1500,
        "re": 100,
        "rent": 0,
        "salaries": 0,
        "services": 0,
    }


def test_current_balances_n():
    assert ledger.income_statement(chart).current_profit() == 200


def test_income_statement():
    assert ledger.income_statement(chart) == IncomeStatement(
        income={"services": 800}, expenses={"salaries": 400, "rent": 200}
    )
