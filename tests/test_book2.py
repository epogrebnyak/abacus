from abacus import BalanceSheet, Chart, IncomeStatement
from abacus.accounting_types import ClosingEntry, Entry

# Create chart of accounts
chart = (
    Chart(
        assets=["cash"],
        equity=["equity"],
        expenses=["salaries", "rent"],
        liabilities=[],
        income=["services"],
    )
    .set_retained_earnings("re")
    .offset("services", ["cashback"])
)


# Account balances are known from previous period end
starting_balances = {"cash": 1400, "equity": 1500, "re": -100}

# Create general ledger and post new entries
book = (
    chart.book(starting_balances)
    .post(debit="rent", credit="cash", amount=200)
    .post(debit="cash", credit="services", amount=825)
    .post(debit="cashback", credit="cash", amount=25)
    .post(debit="salaries", credit="cash", amount=400)
    .close()
)


def test_open_accounts():
    assert book.chart == Chart(
        assets=["cash"],
        expenses=["salaries", "rent"],
        equity=["equity", "re"],
        liabilities=[],
        income=["services"],
    ).set_retained_earnings("re").offset("services", ["cashback"])._set_isa("_profit")


def test_start_entry():
    assert book.starting_balances == dict(
        [("cash", 1400), ("equity", 1500), ("re", -100)],
    )


def test_business_entries():
    assert book.entries.business == [
        Entry(dr="rent", cr="cash", amount=200),
        Entry(dr="cash", cr="services", amount=825),
        Entry(dr="cashback", cr="cash", amount=25),
        Entry(dr="salaries", cr="cash", amount=400),
    ]


def test_adjustment_entries():
    assert book.entries.adjustment == []


def test_closing_entries():
    assert book.entries.closing.contra_income == [
        ClosingEntry(dr="services", cr="cashback", amount=25)
    ]
    assert book.entries.closing.income == [
        ClosingEntry(dr="services", cr="_profit", amount=800)
    ]
    assert book.entries.closing.expense == [
        ClosingEntry(dr="_profit", cr="salaries", amount=400),
        ClosingEntry(dr="_profit", cr="rent", amount=200),
    ]
    assert book.entries.closing.isa == ClosingEntry(dr="_profit", cr="re", amount=200)


def test_after_close_entries():
    assert book.entries.after_close == []


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
