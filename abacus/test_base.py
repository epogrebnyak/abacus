from .from_core import Chart, Entry, make_ledger, process_entries, close, balances

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "re"],
    liabilities=["divp", "payables"],
    income=["sales"],
)

# for future use
handler = dict(retained_earnings="re", cash="cash", dividend_payable="divp")

e1 = Entry(dr="cash", cr="equity", amount=1000)
e2 = Entry(dr="goods_for_sale", cr="cash", amount=250)
e3 = Entry(cr="goods_for_sale", dr="cogs", amount=200)
e4 = Entry(cr="sales", dr="cash", amount=400)
e5 = Entry(cr="cash", dr="sga", amount=50)
entries = [e1, e2, e3, e4, e5]


def test_close_entries():
    ledger = make_ledger(chart)
    # must also test for failed entries
    ledger2 = process_entries(ledger, entries)
    # can show profit here
    ledger3 = close(ledger2, "re")
    # accrue_dividend(ledger, "re", "divp", amount)
    # transfer_dividend(ledger, "divp", "cash")
    assert balances(ledger3) == {
        "cash": 1100,
        "receivables": 0,
        "goods_for_sale": 50,
        "cogs": 0,
        "sga": 0,
        "equity": 1000,
        "re": 150,
        "divp": 0,
        "payables": 0,
        "sales": 0,
        "profit": 0,
    }
