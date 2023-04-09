from abacus.core import (
    Book,
    Chart,
    CreditAccount,
    DebitAccount,
    NamedEntry,
    RawEntry,
    assets,
    balance,
    balances,
    capital,
    dict_sum,
    liabilties,
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
    NamedEntry(name="pay_shareholder_capital", amount=501),
    NamedEntry(name="pay_shareholder_capital", amount=499),
    NamedEntry(name="buy_goods_for_cash", amount=820),
    NamedEntry(name="invoice_buyer", amount=600),
    NamedEntry(name="transfer_goods_sold", amount=360),
    NamedEntry(name="accept_payment", amount=549),
    NamedEntry(name="accrue_salary", amount=400),
    NamedEntry(name="pay_salary", amount=345),
    NamedEntry(name="invoice_buyer", amount=160),
    NamedEntry(name="transfer_goods_sold", amount=80),
    NamedEntry(name="accept_payment", amount=80),
]


def test_reulting_balance():
    book = Book(chart_1, entry_shortcodes_1)
    book.append_named_entries(named_entries_1)
    ledger = book.get_ledger()
    balances_dict = balances(ledger)
    assets_dict = assets(balances_dict, chart_1)
    capital_dict = capital(balances_dict, chart_1)
    liabilities_dict = liabilties(balances_dict, chart_1)
    v = dict_sum(assets_dict)
    cap = dict_sum(capital_dict)
    liab = dict_sum(liabilities_dict)
    assert v == 975
    assert cap == 920
    assert liab == 55
