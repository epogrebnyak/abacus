import pytest
from ui import Chart

from core import (
    T5,
    AbacusError,
    Amount,
    BalanceSheet,
    CreditAccount,
    DebitAccount,
    Entry,
    IncomeStatement,
    Ledger,
    UnrestrictedCreditAccount,
    double_entry,
)


def test_chart_setter_by_default():
    chart = Chart.default()
    assert chart["retained_earnings"] == (T5.Capital, [])
    assert chart.income_summary_account == "__isa__"
    assert chart.retained_earnings_account == "retained_earnings"
    assert chart.names == {}


def test_fast_chart_setter_with_offsets():
    chart = Chart.default()
    chart.set_account("equity", T5.Capital, ["ts"])
    assert chart["equity"] == (T5.Capital, ["ts"])


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
        me = Entry().dr("a", Amount(100)).cr("b", Amount(99))
        me.validate_balance()


def test_chart_on_retained_earnings():
    chart = Chart(income_summary_account="isa", retained_earnings_account="this_is_re")
    assert chart.retained_earnings_account == "this_is_re"
    assert chart.accounts["this_is_re"] == (T5.Capital, [])


def test_balance_sheet_respects_contra_account():
    chart = (
        Chart(income_summary_account="isa", retained_earnings_account="re")
        .add_asset("cash")
        .add_capital("equity", offsets=["treasury_shares"])
    )
    ledger = Ledger.new(chart)
    me = Entry().dr("cash", 100).dr("treasury_shares", 21).cr("equity", 120)
    ledger.post(me)
    bs = BalanceSheet.new(ledger, chart)
    assert bs.capital["equity"] == 99


def test_ledger_post_method():
    book = Ledger({"a": DebitAccount(), "b": CreditAccount()})
    e = Entry(debits=[("a", 100)], credits=[("b", 100)])
    book.post(e)
    assert book == {
        "a": DebitAccount(Amount(100), Amount(0)),
        "b": CreditAccount(Amount(0), Amount(100)),
    }


def test_ledger_copy_is_callable():
    Ledger({"cash": DebitAccount(), "equity": CreditAccount()}).copy()


def test_end_to_end():
    entries = [
        double_entry("cash", "equity", 100),
        double_entry("inventory", "cash", 90),
        double_entry("cogs", "inventory", 60),
        Entry().dr("cash", 75).dr("refunds", 2).cr("sales", 77),
    ]

    chart = Chart(income_summary_account="__isa__", retained_earnings_account="__re__")
    chart.set_retained_earnings("retained_earnings")
    chart.add_asset("cash")
    chart.add_asset("inventory")
    chart.add_capital("equity")
    chart.add_expense("cogs")
    chart.add_income("sales", offsets=["refunds"])

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
        "__isa__": (0, 0),
    }
    income_summary = IncomeStatement.new(ledger, chart)
    assert income_summary.net_earnings == 15
    ledger.close(chart)
    assert ledger.balances() == {
        "cash": 85,
        "inventory": 30,
        "equity": 100,
        "retained_earnings": 15,
    }
