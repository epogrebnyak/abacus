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
    xs[0][0] == "cash"


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
        .close()
    )
# fmt: on


def test_income_statement(simple_book):
    assert simple_book.income_statement.net_earnings == 400
