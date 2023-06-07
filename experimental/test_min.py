from abacus import BalanceSheet, Chart, IncomeStatement
from abacus.accounting_types import BusinessEntry
from abacus.closing_types import CloseExpense, CloseIncome, CloseISA
from abacus.journal import BaseJournal
from abacus.accounts import OpenRegularAccount

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
    chart.journal().start(starting_balances)
    .post(dr="rent", cr="cash", amount=200)
    .post(dr="cash", cr="services", amount=800)
    .post(dr="salaries", cr="cash", amount=400)
    .close()
)


def test_postings():
    assert journal.data == BaseJournal(
        open_accounts=[
            OpenRegularAccount(name="cash", type="Asset"),
            OpenRegularAccount(name="salaries", type="Expense"),
            OpenRegularAccount(name="rent", type="Expense"),
            OpenRegularAccount(name="equity", type="Capital"),
            OpenRegularAccount(name="re", type="RetainedEarnings"),
            OpenRegularAccount(name="services", type="Income"),
            OpenRegularAccount(name="_profit", type="IncomeSummaryAccount"),
        ],
        business_entries=[
            BusinessEntry(dr="rent", cr="cash", amount=200, action="post"),
            BusinessEntry(dr="cash", cr="services", amount=800, action="post"),
            BusinessEntry(dr="salaries", cr="cash", amount=400, action="post"),
        ],
        adjustment_entries=[],
        closing_entries=[
            CloseExpense(
                dr="_profit", cr="salaries", amount=400, action="close_expense"
            ),
            CloseExpense(dr="_profit", cr="rent", amount=200, action="close_expense"),
            CloseIncome(dr="services", cr="_profit", amount=800, action="close_income"),
            CloseISA(dr="_profit", cr="re", amount=200, action="close_isa"),
        ],
        post_close_entries=[],
        is_closed=True,
    )


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
