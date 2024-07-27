import pytest

from playground import (
    AbacusError,
    Account,
    Amount,
    Chart,
    Credit,
    Debit,
    Ledger,
    MultipleEntry,
    Side,
    TAccount,
    close,
    double_entry,
    multiple_entry,
)


def test_invalid_multiple_entry():
    with pytest.raises(AbacusError):
        MultipleEntry(data=[Debit("a", 100), Credit("b", 99)])


def test_ledger_post_method():
    book = Ledger({"a": TAccount(Side.Debit), "b": TAccount(Side.Credit)})
    e = MultipleEntry(data=[Debit("a", 100), Credit("b", 100)])
    book.post(e)
    assert book == {
        "a": TAccount(side=Side.Debit, debits=[Amount(100)], credits=[]),
        "b": TAccount(side=Side.Credit, debits=[], credits=[Amount(100)]),
    }


def test_end_to_end():
    entries = [
        double_entry("cash", "equity", 100),
        double_entry("inventory", "cash", 90),
        double_entry("cogs", "inventory", 60),
        multiple_entry(Debit("cash", 75), Debit("refunds", 2), Credit("sales", 77)),
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
    tb1 = ledger.trial_balance()
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
    tb2 = ledger.trial_balance()
    balances = tb2.balances()
    assert balances == {
        "cash": 85,
        "inventory": 30,
        "equity": 100,
        "retained_earnings": 15,
    }
