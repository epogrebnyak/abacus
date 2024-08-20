import pytest
from ui import Book, NamedEntry, StoredEntry

from core import T5, Amount, CreditEntry, DebitEntry


def test_named_entry_constructor():
    ne = (
        NamedEntry("Shareholder investment")
        .amount(300)
        .debit(account_name="cash")
        .credit(account_name="equity")
    )
    assert ne._entry.debits == [DebitEntry("cash", Amount(300))]
    assert ne._entry.credits == [CreditEntry("equity", Amount(300))]
    assert ne._amount == 300
    assert ne.title == "Shareholder investment"


def test_named_entry_on_None_amount_raises_error():
    with pytest.raises(TypeError):
        NamedEntry("").debit(account_name="cash")


def test_book_add_assets():
    xs = Book("Pied Piper").add_asset("cash").chart[T5.Asset]
    xs[0][0] == "cash"


def test_book():
    assert (
        Book("test")
        .add_asset("cash")
        .add_capital("equity")
        .open()
        .entry("Shareholder investment")
        .amount(1500)
        .debit("cash")
        .credit("equity")
        .commit()
        .entries[-1]
    ) == StoredEntry(
        title="Shareholder investment",
        debits=[("cash", 1500)],
        credits=[("equity", 1500)],
    )
