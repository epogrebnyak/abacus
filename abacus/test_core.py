from abacus.core import (
    Chart,
    CreditAccount,
    DebitAccount,
    Entry,
    balance,
    balances,
    current_profit,
    make_ledger,
    process_entry,
    process_named_entries,
)


def test_balance_on_DebitAccount():
    assert balance(DebitAccount([10, 10], [5])) == 15


def test_balance_on_CreditAccount():
    assert balance(CreditAccount([2, 2], [5, 4])) == 5


chart = Chart(
    assets=["cash", "receivables", "raw", "wip", "finished_goods", "fixed_assets"],
    expenses=["cogs", "sga", "interest"],
    equity=["equity", "retained_earnings"],
    liabilities=["debt", "accrued_interest", "payables"],
    income=["sales"],
    contraccounts=["depreciation"],
)

named_entries_dict = dict(
    add_capital=("cash", "equity"),
    buy_ppe=("fixed_assets", "cash"),
    invoice_raw=("raw", "payables"),
    pay_raw=("payables", "cash"),
    to_wip=("wip", "raw"),
    add_labor=("wip", "payables"),
    pay_labor=("payables", "cash"),
    accrue_depr=("wip", "depreciation"),
    to_finished=("finished_goods", "wip"),
    invoice_sale=("receivables", "sales"),
    register_cogs=("cogs", "finished_goods"),
    accept_payment=("cash", "receivables"),
)

named_entries = [
    ("add_capital", 2500),
    ("buy_ppe", 1200),
    ("invoice_raw", 800),
    ("pay_raw", 800),
    ("to_wip", 750),
    ("add_labor", 150),
    ("pay_labor", 150),
    ("accrue_depr", 100),
    ("to_finished", 1000),
    ("invoice_sale", 1800),
    ("register_cogs", 900),
    ("accept_payment", 800),
    ("invoice_raw", 700),
    ("pay_raw", 700),
]


def test_ledger():
    ledger = make_ledger(chart)
    ledger = process_entry(ledger, Entry("cash", "equity", 1000))
    assert ledger["cash"] == DebitAccount([1000], [])
    assert ledger["equity"] == CreditAccount([], [1000])


def process_ledger():
    ledger = make_ledger(chart)
    return process_named_entries(ledger, named_entries_dict, named_entries)


def test_balances():
    ledger = process_ledger()
    assert balances(ledger) == {
        "accrued_interest": 0,
        "cash": 450,
        "cogs": 900,
        "debt": 0,
        "depreciation": 100,
        "equity": 2500,
        "finished_goods": 100,
        "fixed_assets": 1200,
        "interest": 0,
        "payables": 0,
        "raw": 750,
        "receivables": 1000,
        "retained_earnings": 0,
        "sales": 1800,
        "sga": 0,
        "wip": 0,
    }


def test_current_profit():
    ledger = process_ledger()
    assert current_profit(ledger, chart) == 900
