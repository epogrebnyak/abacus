from abacus import Chart, Ledger, __version__
from abacus.accounting import (CreditAccount, DebitAccount, make_book,
                               make_ledger, to_entry)


def test_version():
    assert __version__ == "0.0.0"


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
        capital=["eq"],
        liabilities=["debt", "ai"],
        income=["sales"],
    )


def test_book():
    chart = Chart(
        assets=["cash", "inv"],
        expenses=["cogs"],
        capital=["eq"],
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
        capital=["eq"],
        liabilities=["debt", "ai"],
        income=["sales"],
    )
    book = make_book(chart)
    entries_doc = """
    100 cash eq
    50 cash debt
    120 inv cash
    120 cogs inv
    135 cash sales 
    5 interest ai
    5 ai cash
    """
    entries = [
        to_entry(textline) for textline in entries_doc.split("\n") if textline.strip()
    ]
    book.process_all(entries)
    assert book.profit == 10
    return book
