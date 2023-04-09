from abacus import Book, Chart, RawEntry, BalanceSheet

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    liabilities=["payables"],
    income=["sales"],
)

# Example with raw entries

book = Book(chart)
e1 = RawEntry(dr="cash", cr="equity", amount=1000)
e2 = RawEntry(dr="goods_for_sale", cr="cash", amount=250)
book.append_raw_entry(e1)
book.append_raw_entry(e2)
print(book.get_ledger())
print(book.get_balance_sheet())

# Example with named entries

named_entry_shortcodes = dict(
    pay_shareholder_capital=("cash", "equity"),
    buy_goods_for_cash=("goods_for_sale", "cash"),
    invoice_buyer=("receivables", "sales"),
    transfer_goods_sold=("cogs", "goods_for_sale"),
    accept_payment=("cash", "receivables"),
    accrue_salary=("sga", "payables"),
    pay_salary=("payables", "cash"),
)

named_entries = [
    # start a company
    ("pay_shareholder_capital", 501),
    ("pay_shareholder_capital", 499),
    # acquire goods
    ("buy_goods_for_cash", 820),
    # one order
    ("invoice_buyer", 600),
    ("transfer_goods_sold", 360),
    ("accept_payment", 549),
    # pay labor
    ("accrue_salary", 400),
    ("pay_salary", 345),
    # another order
    ("invoice_buyer", 160),
    ("transfer_goods_sold", 80),
    ("accept_payment", 80),
]

book = Book(chart, named_entry_shortcodes)
book.append_named_entries(named_entries)
print(book.get_ledger())
balance_sheet = book.get_balance_sheet()
print(balance_sheet)

assert balance_sheet == BalanceSheet(
    assets={"cash": 464, "receivables": 131, "goods_for_sale": 380},
    capital={"equity": 1000, "current_profit": -80},
    liabilities={"payables": 55},
)
