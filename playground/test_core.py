import pytest

from core import (
    T5,
    AbacusError,
    Amount,
    BalanceSheet,
    Chart,
    CreditAccount,
    DebitAccount,
    DebitOrCreditAccount,
    Entry,
    IncomeStatement,
    Ledger,
    UnrestrictedCreditAccount,
    double_entry,
)


def test_cd_creates():
    cd = Chart("isa", "re")
    cd.set(T5.Asset, "cash")
    cd.set(T5.Capital, "equity")
    cd.dry_run()
    assert True


def test_account_copy_acts_as_deepcopy():
    da = DebitAccount(Amount(100), Amount(0))
    net = da.copy()
    net.debit(Amount(1))
    assert net.left == Amount(101)
    assert da.left == Amount(100)


def test_temporary_accounts():
    cd = Chart("isa", "re")
    cd.set(T5.Income, "sales")
    cd.offset("sales", "refunds")
    assert cd.temporary_accounts == {"sales", "refunds", "isa"}


def test_closing_pairs():
    cd = Chart("isa", "re")
    cd.set(T5.Asset, "cash")
    cd.set(T5.Capital, "equity")
    cd.offset("equity", "treasury_shares")
    cd.set(T5.Liability, "vat")
    cd.set(T5.Income, "sales")
    cd.offset("sales", "refunds")
    cd.offset("sales", "voids")
    cd.set(T5.Expense, "salaries")
    assert cd.closing_pairs == [
        ("refunds", "sales"),
        ("voids", "sales"),
        ("sales", "isa"),
        ("salaries", "isa"),
        ("isa", "re"),
    ]


def test_fast_chart_setter_with_offsets():
    chart_dict = Chart("isa", "re")
    chart_dict.set(T5.Capital, "equity")
    chart_dict.offset("equity", "ts")
    assert chart_dict.accounts["equity"] == T5.Capital
    assert chart_dict.contra_accounts["ts"] == "equity"


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


def test_chart_dict_elevate_on_empty_dict():
    chart = Chart(
        income_summary_account="isa",
        retained_earnings_account="this_is_re",
    )
    assert chart.closing_pairs == [("isa", "this_is_re")]
    assert chart.accounts["this_is_re"] == T5.Capital
    assert chart._ledger_dict["isa"] == DebitOrCreditAccount
    assert chart.temporary_accounts == {"isa"}


def test_balance_sheet_respects_contra_account():
    chart = Chart(
        income_summary_account="isa",
        retained_earnings_account="re",
    )
    chart.set(T5.Asset, "cash")
    chart.set(T5.Capital, "equity")
    chart.offset("equity", "treasury_shares")
    ledger = Ledger.new(chart)
    ledger.post_many(
        [
            double_entry("cash", "equity", 120),
            double_entry("treasury_shares", "cash", 21),
        ]
    )
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

    chart = Chart("__isa__", "retained_earnings")
    chart.set(T5.Asset, "cash")
    chart.set(T5.Asset, "inventory")
    chart.set(T5.Capital, "equity")
    chart.set(T5.Expense, "cogs")
    chart.set(T5.Income, "sales")
    chart.offset("sales", "refunds")
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
