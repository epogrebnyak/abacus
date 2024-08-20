import pytest

from core import (
    AbacusError,
    Account,
    Amount,
    BalanceSheet,
    Chart,
    CreditAccount,
    CreditEntry,
    DebitAccount,
    DebitEntry,
    DoubleEntry,
    Ledger,
    MultipleEntry,
    UnrestrictedCreditAccount,
    close,
)


def test_debit_account_stays_positive():
    with pytest.raises(AbacusError):
        DebitAccount(Amount(100), 0).credit(Amount(101))


def test_crediting_works_on_credit_account():
    ca = CreditAccount(left=Amount(0), right=Amount(0))
    ca.credit(Amount(100))
    assert ca == CreditAccount(Amount(0), Amount(100))


def test_unrestircted_credit_account_may_be_negative():
    ca = UnrestrictedCreditAccount(left=Amount(0), right=Amount(10))
    ca.debit(Amount(15))
    assert ca.balance == -5


def test_invalid_multiple_entry():
    with pytest.raises(AbacusError):
        me = MultipleEntry([DebitEntry("a", Amount(100)), CreditEntry("b", Amount(99))])
        me.validate()


def test_balance_sheet_on_contra_account():
    chart = Chart(
        assets=[Account("cash")], capital=[Account("equity", ["treasury_shares"])]
    )
    ledger = Ledger.new(chart)
    me = (
        MultipleEntry()
        .debit("cash", 100)
        .credit("equity", 120)
        .debit("treasury_shares", 20)
    )
    ledger.post(me)
    bs = BalanceSheet.new(ledger, chart)
    assert bs.capital["equity"] == 100


def test_ledger_post_method():
    book = Ledger({"a": DebitAccount(), "b": CreditAccount()})
    e = MultipleEntry().dr("a", 100).cr("b", 100)
    book.post(e)
    assert book == {
        "a": DebitAccount(Amount(100), Amount(0)),
        "b": CreditAccount(Amount(0), Amount(100)),
    }


def test_ledger_copy():
    Ledger({"cash": DebitAccount(), "equity": CreditAccount()}).copy()


def test_end_to_end():
    entries = [
        DoubleEntry("cash", "equity", 100),
        DoubleEntry("inventory", "cash", 90),
        DoubleEntry("cogs", "inventory", 60),
        MultipleEntry().dr("cash", 75).dr("refunds", 2).cr("sales", 77),
    ]

    chart = Chart(
        income_summary_account="isa",
        assets=[Account("cash"), Account("inventory")],
        capital=[Account("equity")],
        expenses=[Account("cogs")],
        income=[Account("sales", contra_accounts=["refunds"])],
    ).set_retained_earnings(account_name="retained_earnings")

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
    _, ledger, income_summary = close(ledger, chart, chart.retained_earnings_account)
    assert income_summary.net_earnings == 15
    tb2 = ledger.trial_balance
    balances = tb2.amounts()
    assert balances == {
        "cash": 85,
        "inventory": 30,
        "equity": 100,
        "retained_earnings": 15,
    }
