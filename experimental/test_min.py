from abacus import BalanceSheet, Chart, IncomeStatement
from abacus.accounting_types import (
    BusinessEntry,
    CloseExpense,
    CloseIncome,
    CloseISA,
    OpenAccount,
)

# Create chart of accounts
chart = Chart(
    assets=["cash"],
    equity=["equity"],
    retained_earnings_account="re",
    expenses=["salaries", "rent"],
    income=["services"],
)

# Account balances are known from previous period end
starting_balances = {"cash": 1400, "equity": 1500, "re": -100}

# Create general ledger and post new entries
journal = (
    chart.journal(**starting_balances)
    .post(dr="rent", cr="cash", amount=200)
    .post(dr="cash", cr="services", amount=800)
    .post(dr="salaries", cr="cash", amount=400)
    .close()
)


def test_postings():
    assert journal.data == [
        OpenAccount(name="cash", type="Asset", balance=1400, link=None),
        OpenAccount(
            name="salaries",
            type="Expense",
            balance=0,
            link=None,
        ),
        OpenAccount(name="rent", type="Expense", balance=0, link=None),
        OpenAccount(
            name="equity",
            type="Capital",
            balance=1500,
            link=None,
        ),
        OpenAccount(
            name="re",
            type="RetainedEarnings",
            balance=-100,
            link=None,
        ),
        OpenAccount(
            name="services",
            type="Income",
            balance=0,
            link=None,
        ),
        OpenAccount(
            name="_profit",
            type="IncomeSummaryAccount",
            balance=0,
            link=None,
        ),
        BusinessEntry(dr="rent", cr="cash", amount=200, action="post"),
        BusinessEntry(dr="cash", cr="services", amount=800, action="post"),
        BusinessEntry(dr="salaries", cr="cash", amount=400, action="post"),
        CloseExpense(dr="_profit", cr="salaries", amount=400, action="close_expense"),
        CloseExpense(dr="_profit", cr="rent", amount=200, action="close_expense"),
        CloseIncome(dr="services", cr="_profit", amount=800, action="close_income"),
        CloseISA(dr="_profit", cr="re", amount=200, action="close_isa"),
    ]


def test_balance_sheet():
    assert journal.balance_sheet() == BalanceSheet(
        assets={"cash": 1600}, capital={"equity": 1500, "re": 100}, liabilities={}
    )


def test_balances():
    assert journal.balances() == {
        "_profit": 0,
        "cash": 1600,
        "equity": 1500,
        "re": 100,
        "rent": 0,
        "salaries": 0,
        "services": 0,
    }


def test_current_balances_n():
    assert journal.current_profit() == 200


def test_income_statement():
    assert journal.income_statement() == IncomeStatement(
        income={"services": 800}, expenses={"salaries": 400, "rent": 200}
    )
