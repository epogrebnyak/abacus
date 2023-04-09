# pylint: disable=missing-docstring

from abacus.core import (
    Book,
    Chart,
    CreditAccount,
    DebitAccount,
    RawEntry,
    BalanceSheet,
    balance,
    make_ledger,
    process_raw_entry,
)


def test_balance_on_DebitAccount():
    assert balance(DebitAccount([10, 10], [5])) == 15


def test_balance_on_CreditAccount():
    assert balance(CreditAccount([2, 2], [5, 4])) == 5


def test_ledger():
    ledger = make_ledger(chart_1)
    ledger = process_raw_entry(ledger, RawEntry("cash", "equity", 1000))
    assert ledger["cash"] == DebitAccount([1000], [])
    assert ledger["equity"] == CreditAccount([], [1000])


chart_1 = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "retained_earnings"],
    liabilities=["payables"],
    income=["sales"],
)

entry_shortcodes_1 = dict(
    pay_shareholder_capital=("cash", "equity"),
    buy_goods_for_cash=("goods_for_sale", "cash"),
    invoice_buyer=("receivables", "sales"),
    transfer_goods_sold=("cogs", "goods_for_sale"),
    accept_payment=("cash", "receivables"),
    accrue_salary=("sga", "payables"),
    pay_salary=("payables", "cash"),
)

named_entries_1 = [
    ("pay_shareholder_capital", 501),
    ("pay_shareholder_capital", 499),
    ("buy_goods_for_cash", 820),
    ("invoice_buyer", 600),
    ("transfer_goods_sold", 360),
    ("accept_payment", 549),
    ("accrue_salary", 400),
    ("pay_salary", 345),
    ("invoice_buyer", 160),
    ("transfer_goods_sold", 80),
    ("accept_payment", 80),
]


def balance_sheet():
    return (
        Book(chart_1, entry_shortcodes_1)
        .append_named_entries(named_entries_1)
        .get_balance_sheet()
    )


def test_balance_sheet():
    bs = balance_sheet()
    assert bs == BalanceSheet(
        assets={"cash": 464, "receivables": 131, "goods_for_sale": 380},
        capital={"equity": 1000, "retained_earnings": 0, "current_profit": -80},
        liabilities={"payables": 55},
    )


def test_balance_sheet_totals():
    bs = balance_sheet()
    assert bs.total_assets == 975
    assert bs.total_capital == 920
    assert bs.total_liabilities == 55


def test_balance_sheet_totals_sum_up():
    bs = balance_sheet()
    assert bs.is_valid() is True
