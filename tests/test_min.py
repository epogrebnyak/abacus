from abacus import BalanceSheet, Chart, IncomeStatement
from abacus.accounting_types import Entry
from abacus.closing_types import CloseContraIncome, CloseExpense, CloseIncome, CloseISA

# Create chart of accounts
chart = Chart(
    assets=["cash"],
    equity=["equity"],
    retained_earnings_account="re",
    expenses=["salaries", "rent"],
    liabilities=[],
    income=["services"],
    contra_accounts={"services": ["cashback"]},
)

# Account balances are known from previous period end
starting_balances = {"cash": 1400, "equity": 1500, "re": -100}

# Create general ledger and post new entries
book = (
    chart.book(starting_balances)
    .post(dr="rent", cr="cash", amount=200)
    .post(dr="cash", cr="services", amount=825)
    .post(dr="cashback", cr="cash", amount=25)
    .post(dr="salaries", cr="cash", amount=400)
    .close()
)


def test_open_accounts():
    assert book.chart == Chart(
        assets=["cash"],
        expenses=["salaries", "rent"],
        equity=["equity"],
        retained_earnings_account="re",
        liabilities=[],
        income=["services"],
        contra_accounts={"services": ["cashback"]},
        income_summary_account="_profit",
    )


def test_start_entry():
    assert book.starting_balances == dict(
        [("cash", 1400), ("equity", 1500), ("re", -100)],
    )


def test_business_entries():
    assert book.entries.business == [
        Entry(dr="rent", cr="cash", amount=200, action="post"),
        Entry(dr="cash", cr="services", amount=825, action="post"),
        Entry(dr="cashback", cr="cash", amount=25, action="post"),
        Entry(dr="salaries", cr="cash", amount=400, action="post"),
    ]


def test_adjustment_entries():
    assert book.entries.adjustment == []


def test_closing_entries():
    assert book.entries.closing == [
        CloseContraIncome(
            dr="services", cr="cashback", amount=25, action="close_contra_income"
        ),
        CloseIncome(dr="services", cr="_profit", amount=800, action="close_income"),
        CloseExpense(dr="_profit", cr="salaries", amount=400, action="close_expense"),
        CloseExpense(dr="_profit", cr="rent", amount=200, action="close_expense"),
        CloseISA(dr="_profit", cr="re", amount=200, action="close_isa"),
    ]


def test_post_close_entries():
    assert book.entries.post_close == []


def test_post_is_closed():
    assert book.is_closed


def test_balance_sheet():
    assert book.balance_sheet() == BalanceSheet(
        assets={"cash": 1600}, capital={"equity": 1500, "re": 100}, liabilities={}
    )


def test_balances():
    assert book.balances() == {
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
    assert book.income_statement().current_profit() == 200


def test_income_statement():
    assert book.income_statement() == IncomeStatement(
        income={"services": 800}, expenses={"salaries": 400, "rent": 200}
    )
