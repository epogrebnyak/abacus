import pytest
from ui import Book, NamedEntry

from core import T5, Amount


def test_named_entry_constructor():
    ne = (
        NamedEntry(title="Shareholder investment")
        .amount(300)
        .debit(account_name="cash")
        .credit(account_name="equity")
    )
    assert ne.debits == [("cash", Amount(300))]
    assert ne.credits == [("equity", Amount(300))]
    assert ne.title == "Shareholder investment"


def test_named_entry_on_None_amount_raises_error():
    with pytest.raises(TypeError):
        NamedEntry().debit(account_name="cash")


def test_book_add_assets():
    xs = Book("Pied Piper").add_asset("cash").chart[T5.Asset]
    xs[0] == ("cash", [])


def test_book():
    entry = (
        Book("test")
        .add_asset("cash")
        .add_capital("equity")
        .open()
        .entry("Shareholder investment")
        .amount(1500)
        .debit("cash")
        .credit("equity")
        .commit()
        .entries.saved[-1]
    )
    assert entry == NamedEntry(
        title="Shareholder investment",
        debits=[("cash", Amount(1500))],
        credits=[("equity", Amount(1500))],
    )


# fmt: off
@pytest.fixture
def simple_book():
       return (
        Book("Simple Book, Inc.")
        .add_asset("cash")
        .add_capital("equity")
        .add_income("sales")
        .add_expense("salary")
        .open()
        .entry("Shareholder investment").amount(1500).debit("cash").credit("equity").commit()
        .entry("Provided services").amount(800).debit("cash").credit("sales").commit()
        .entry("Paid wages").amount(400).debit("salary").credit("cash").commit()
    )
# fmt: on


def test_book_is_closed(simple_book):
    assert simple_book.is_closed() is False
    assert simple_book.close().is_closed() is True


def test_income_statement_before_close(simple_book):
    assert simple_book.income_statement.net_earnings == 400


def test_income_statement_after_close(simple_book):
    assert simple_book.close().income_statement.net_earnings == 400


def test_balance_sheet_before_close(simple_book):
    assert simple_book.balance_sheet.assets["cash"] == 1900
    assert simple_book.balance_sheet.capital["equity"] == 1500
    assert (
        simple_book.balance_sheet.capital["retained_earnings"] == 0
    )  # may need proxy value of 400
    assert simple_book.balance_sheet.liabilities == {}


def test_balance_sheet_after_close(simple_book):
    assert simple_book.close().balance_sheet.assets["cash"] == 1900
    assert simple_book.balance_sheet.capital["equity"] == 1500
    assert simple_book.balance_sheet.capital["retained_earnings"] == 400
    assert simple_book.balance_sheet.liabilities == {}


def test_trial_balance_before_close(simple_book):
    assert simple_book.trial_balance.tuples() == {
        "cash": (1900, 0),
        "equity": (0, 1500),
        "sales": (0, 800),
        "salary": (400, 0),
        "__isa__": (0, 0),
        "retained_earnings": (0, 0),
    }


def test_trial_balance_after_close(simple_book):
    assert simple_book.close().trial_balance.tuples() == {
        "cash": (1900, 0),
        "equity": (0, 1500),
        "retained_earnings": (0, 400),
    }
