from abacus import BalanceSheet, Chart, IncomeStatement
from abacus.accounting_types import (
    BusinessEntry,
    CreditEntry,
    DebitEntry,
    MultipleEntry,
)
from abacus.accounts import OpenAccount
from abacus.closing_types import CloseContraIncome, CloseExpense, CloseIncome, CloseISA

# Create chart of accounts
chart = Chart(
    assets=["cash"],
    equity=["equity"],
    retained_earnings_account="re",
    expenses=["salaries", "rent"],
    income=["services"],
    contra_accounts={"services": ["cashback"]},
)

# Account balances are known from previous period end
starting_balances = {"cash": 1400, "equity": 1500, "re": -100}

# Create general ledger and post new entries
journal = (
    chart.journal(starting_balances)
    .post(dr="rent", cr="cash", amount=200)
    .post(dr="cash", cr="services", amount=825)
    .post(dr="cashback", cr="cash", amount=25)
    .post(dr="salaries", cr="cash", amount=400)
    .close()
)


def test_netting():
    assert journal.data.netting == {"services": ["cashback"]}


def test_open_accounts():
    assert journal.data.open_accounts == [
        OpenAccount(name="cash", type="Asset"),
        OpenAccount(name="salaries", type="Expense"),
        OpenAccount(name="rent", type="Expense"),
        OpenAccount(name="equity", type="Capital"),
        OpenAccount(name="re", type="RetainedEarnings"),
        OpenAccount(name="services", type="Income"),
        OpenAccount(name="_profit", type="IncomeSummaryAccount"),
        OpenAccount(name="cashback", type="ContraIncome"),
    ]


def test_start_entry():
    assert journal.data.start_entry == MultipleEntry(
        [DebitEntry("cash", 1400)],
        [CreditEntry("equity", 1500), CreditEntry("re", -100)],
    )


def test_business_entries():
    assert journal.data.business_entries == [
        BusinessEntry(dr="rent", cr="cash", amount=200, action="post"),
        BusinessEntry(dr="cash", cr="services", amount=825, action="post"),
        BusinessEntry(dr="cashback", cr="cash", amount=25, action="post"),
        BusinessEntry(dr="salaries", cr="cash", amount=400, action="post"),
    ]


def test_adjustment_entries():
    assert journal.data.adjustment_entries == []


def test_closing_entries():
    assert journal.data.closing_entries == [
        CloseContraIncome(
            dr="services", cr="cashback", amount=25, action="close_contra_income"
        ),
        CloseIncome(dr="services", cr="_profit", amount=800, action="close_income"),
        CloseExpense(dr="_profit", cr="salaries", amount=400, action="close_expense"),
        CloseExpense(dr="_profit", cr="rent", amount=200, action="close_expense"),
        CloseISA(dr="_profit", cr="re", amount=200, action="close_isa"),
    ]


def test_post_close_entries():
    assert journal.data.post_close_entries == []


def test_post_is_closed():
    assert journal.data.is_closed is True


def test_balance_sheet():
    assert journal.balance_sheet() == BalanceSheet(
        assets={"cash": 1600}, capital={"equity": 1500, "re": 100}, liabilities={}
    )


def test_balances():
    assert journal.balances() == {
        "_profit": 0,
        "cashback": 0,
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
