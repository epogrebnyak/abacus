import pytest

from core import (
    T5,
    AbacusError,
    Amount,
    BalanceSheet,
    Chart,
    ChartDict,
    Contra,
    CreditAccount,
    DebitAccount,
    DebitOrCreditAccount,
    Entry,
    IncomeStatement,
    Just,
    Ledger,
    Regular,
    UnrestrictedCreditAccount,
    double_entry,
)


def test_chart_validate():
    cd = ChartDict()
    cd.set(T5.Asset, "cash")
    cd.set(T5.Capital, "equity")
    chart = Chart(cd, [("refunds", "sales")])
    with pytest.raises(AbacusError) as e:
        chart.validate()
    assert str(e.value).replace("'", "") == "refunds"


def test_chart_validate_on_non_existent_contra_account():
    cd = ChartDict()
    cd["refunds"] = Contra("sales")
    chart = Chart(cd, [])
    with pytest.raises(AbacusError) as e:
        chart.validate()
    assert str(e.value).replace("'", "") == "sales"


def test_account_copy_acts_deepcopy():
    da = DebitAccount(Amount(100), Amount(0))
    net = da.copy()
    net.debit(Amount(1))
    assert net.left == Amount(101)
    assert da.left == Amount(100)


def test_temporary_accounts():
    cd = ChartDict()
    cd.set(T5.Income, "sales")
    cd.offset("sales", "refunds")
    chart = cd.qualify(income_summary_account="isa", retained_earnings_account="re")
    assert chart.temporary_accounts == {"sales", "refunds", "isa"}


def test_closing_pairs():
    cd = ChartDict()
    cd.set(T5.Asset, "cash")
    cd.set(T5.Capital, "equity")
    cd.offset("equity", "treasury_shares")
    cd.set(T5.Liability, "vat")
    cd.set(T5.Income, "sales")
    cd.offset("sales", "refunds")
    cd.offset("sales", "voids")
    cd.set(T5.Expense, "salaries")
    assert list(cd.closing_pairs("isa", "re")) == [
        ("refunds", "sales"),
        ("voids", "sales"),
        ("sales", "isa"),
        ("salaries", "isa"),
        ("isa", "re"),
    ]


def test_fast_chart_setter_with_offsets():
    chart_dict = ChartDict()
    chart_dict.set(T5.Capital, "equity")
    chart_dict.offset("equity", "ts")
    assert chart_dict.data["equity"] == Regular(T5.Capital)
    assert chart_dict.data["ts"] == Contra("equity")


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
    chart = ChartDict().qualify(
        income_summary_account="isa",
        retained_earnings_account="this_is_re",
    )
    assert chart.closing_pairs == [("isa", "this_is_re")]
    assert chart.accounts["this_is_re"] == Regular(T5.Capital)
    assert chart.accounts["isa"] == Just(DebitOrCreditAccount)
    assert chart.temporary_accounts == {"isa"}
    assert len(chart.accounts) == 2


def test_balance_sheet_respects_contra_account():
    accounts = ChartDict()
    accounts.set(T5.Asset, "cash")
    accounts.set(T5.Capital, "equity")
    accounts.offset("equity", "treasury_shares")
    chart = accounts.qualify(
        income_summary_account="isa",
        retained_earnings_account="re",
    )
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

    accounts = ChartDict()
    accounts.set(T5.Asset, "cash")
    accounts.set(T5.Asset, "inventory")
    accounts.set(T5.Capital, "equity")
    accounts.set(T5.Expense, "cogs")
    accounts.set(T5.Income, "sales")
    accounts.offset("sales", "refunds")
    chart = accounts.qualify(
        income_summary_account="__isa__", retained_earnings_account="retained_earnings"
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
