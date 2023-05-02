# pylint: disable=missing-docstring

from abacus.core import (
    AccountBalanceDict,
    BalanceSheet,
    Book,
    Chart,
    CreditAccount,
    DebitAccount,
    EntryShortcodes,
    RawEntry,
    balance,
    make_ledger,
    process_raw_entry,
    closing_entries
)


def test_balance_on_DebitAccount():
    assert balance(DebitAccount([10, 10], [5])) == 15


def test_balance_on_CreditAccount():
    assert balance(CreditAccount([2, 2], [5, 4])) == 5


def test_AccountBalanceDict():
    assert (
        AccountBalanceDict(
            [
                ("a", 3),
                ("b", -1),
            ]
        ).total()
        == 2
    )



from abacus import IncomeStatement, BalanceSheet, Book, Chart, EntryShortcodes, RawEntry

def chart2():
    return Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
)

def ledger2():
    chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
)
    book = Book(chart)
    e1 = RawEntry(dr="cash", cr="equity", amount=1000)
    e2 = RawEntry(dr="goods_for_sale", cr="cash", amount=250)
    e3 = RawEntry(cr="goods_for_sale", dr="cogs", amount=200)
    e4 = RawEntry(cr="sales", dr="cash", amount=400)
    e5 = RawEntry(cr="cash", dr="sga", amount=50)
    book.append_raw_entries([e1, e2, e3, e4, e5])
    return book.get_ledger()

def test_closing_entries():
    ledger = ledger2()
    chart = chart2()
    assert closing_entries(ledger, chart, "re") == [
        RawEntry(dr="sales", cr="profit", amount=400),
        RawEntry(dr="profit", cr="cogs", amount=200),
        RawEntry(dr="profit", cr="sga", amount=50),
        RawEntry(dr="profit", cr="re", amount=150),
    ]


def test_statements():
# %%
    ledger = ledger2()
    chart = chart2()
    income_st, ledger = ledger.close_entries(chart, "re")
    assert income_st == IncomeStatement(
        income={"sales": 400}, expenses={"cogs": 200, "sga": 50}
    )
    ledger = ledger.accrue_dividend(75, "re", "divp").disburse_dividend("divp", "cash")
    balance_st = ledger.balance_sheet(chart)
    assert balance_st == BalanceSheet(
        assets={"cash": 1025, "receivables": 0, "goods_for_sale": 50},
        capital={"equity": 1000, "re": 75},
        liabilities={"divp": 0, "payables": 0},
    )




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
    inc, ledger = (
        Book(chart_1, EntryShortcodes(entry_shortcodes_1))
        .append_named_entries(named_entries_1)
        .get_ledger()
        .close_entries(chart_1, "retained_earnings")
    )
    return ledger.balance_sheet(chart_1)



def test_balance_sheet():
    assert balance_sheet() == BalanceSheet(
        assets={"cash": 464, "receivables": 131, "goods_for_sale": 380},
        capital={"equity": 1000, "retained_earnings": -80},
        liabilities={"payables": 55},
    )


def test_balance_sheet_totals():
    bs = balance_sheet()
    assert bs.assets.total() == 975
    assert bs.capital.total() == 920
    assert bs.liabilities.total() == 55


def test_balance_sheet_totals_sum_up():
    bs = balance_sheet()
    assert bs.is_valid() is True
