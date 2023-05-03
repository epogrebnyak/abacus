from abacus import Chart, Ledger
from abacus.remove.accounting import CreditAccount, DebitAccount, make_ledger
from abacus.remove.formatting import make_book

names = dict(
    inv="Inventory",
    cogs="Cost of goods sold (COGS)",
    ai="Accrued interest",
    eq="Equity",
)


def test_chart():
    assets = "cash inv".split()
    expenses = ["cogs"]
    capital = ["eq"]
    liabilities = "debt ai".split()
    income = ["sales"]
    chart = Chart(assets, expenses, capital, liabilities, income)
    assert chart == Chart(
        assets=["cash", "inv"],
        expenses=["cogs"],
        equity=["eq"],
        liabilities=["debt", "ai"],
        income=["sales"],
    )


def test_book():
    chart = Chart(
        assets=["cash", "inv"],
        expenses=["cogs"],
        equity=["eq"],
        liabilities=["debt", "ai"],
        income=["sales"],
    )
    assert make_ledger(chart) == Ledger(
        accounts={  # fmt: off
            "cash": DebitAccount(debits=[], credits=[]),
            "inv": DebitAccount(debits=[], credits=[]),
            "cogs": DebitAccount(debits=[], credits=[]),
            "debt": CreditAccount(debits=[], credits=[]),
            "ai": CreditAccount(debits=[], credits=[]),
            "eq": CreditAccount(debits=[], credits=[]),
            "sales": CreditAccount(debits=[], credits=[]),
        }  # fmt: on
    )


def test_book_balance():
    chart = Chart(
        assets=["cash", "inv"],
        expenses=["cogs", "interest"],
        equity=["eq"],
        liabilities=["debt", "ai"],
        income=["sales"],
    )
