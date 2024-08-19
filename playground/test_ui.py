import pytest
from ui import Book, NamedEntry

from core import AbacusError, Amount, CreditEntry, DebitEntry


def test_book_add_assets():
    assert Book("Pied Piper").add_assets("cash").chart.assets[0].name == "cash"


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
    with pytest.raises(AbacusError):
        NamedEntry("").debit(account_name="cash")
