import pytest
from ui import NamedEntry
from core import DebitEntry, Amount, CreditEntry, AbacusError


def test_named_entry_constructor():
    ne = (
        NamedEntry("Shareholder investment")
        .amount(300)
        .debit(account_name="cash")
        .credit(account_name="equity")
    )
    assert ne._unbalanced_entry.data == [
        DebitEntry("cash", Amount(300)),
        CreditEntry("equity", Amount(300)),
    ]
    assert ne._amount == 300
    assert ne.title == "Shareholder investment"


def test_named_entry_on_None_amount():
    with pytest.raises(AbacusError):
        NamedEntry("").debit(account_name="cash")
