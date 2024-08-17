import pytest

from core import (
    AbacusError,
    Account,
    Amount,
    Chart,
    CreditEntry,
    DebitEntry,
    Ledger,
    Side,
    close,
    DoubleEntry,
    MultipleEntry,
    DebitAccount,
    CreditAccount,
)


def test_debit_account_stays_positive():
    with pytest.raises(AbacusError):
        DebitAccount(Amount(100), 0).credit(Amount(101))


def test_unrestircted_credit_account_may_be_negative():
    CreditAccount().credit(Amount(5))


def test_invalid_multiple_entry():
    with pytest.raises(AbacusError):
        me = MultipleEntry([DebitEntry("a", Amount(100)), CreditEntry("b", Amount(99))])
        me.validate()


def test_ledger_post_method():
    book = Ledger({"a": DebitAccount(), "b": CreditAccount()})
    e = MultipleEntry.new(DebitEntry("a", 100), CreditEntry("b", 100))
    book.post(e)
    assert book == {
        "a": DebitAccount(Amount(100), Amount(0)),
        "b": CreditAccount(Amount(0), Amount(100)),
    }


def test_end_to_end():
    entries = [
        DoubleEntry("cash", "equity", 100),
        DoubleEntry("inventory", "cash", 90),
        DoubleEntry("cogs", "inventory", 60),
        MultipleEntry.new(
            DebitEntry("cash", 75), DebitEntry("refunds", 2), CreditEntry("sales", 77)
        ),
    ]

    chart = Chart(
        income_summary_account="isa",
        retained_earnings_account="retained_earnings",
        assets=[Account("cash"), Account("inventory")],
        capital=[Account("equity")],
        expenses=[Account("cogs")],
        income=[Account("sales", contra_accounts=["refunds"])],
    )

    ledger = Ledger.new(chart)
    ledger.post_many(entries)
    tb1 = ledger.trial_balance
    assert tb1.tuples() == {
        "cash": (85, 0),
        "inventory": (30, 0),
        "equity": (0, 100),
        "retained_earnings": (0, 0),
        "sales": (0, 77),
        "refunds": (2, 0),
        "cogs": (60, 0),
        "isa": (0, 0),
    }
    _, ledger, income_summary = close(ledger, chart)
    assert income_summary.net_earnings == 15
    tb2 = ledger.trial_balance
    balances = tb2.amounts()
    assert balances == {
        "cash": 85,
        "inventory": 30,
        "equity": 100,
        "retained_earnings": 15,
    }
