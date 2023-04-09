from abacus import Book, Chart, BalanceSheet

chart = Chart(
    assets=["cash", "receivables", "goods_for_sale"],
    expenses=["cogs", "sga"],
    equity=["equity", "retained_earnings"],
    liabilities=["payables"],
    income=["sales"],
)

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
balance_sheet = book.get_balance_sheet()
print(balance_sheet)

assert balance_sheet == BalanceSheet(
    assets={"cash": 464, "receivables": 131, "goods_for_sale": 380},
    capital={"equity": 1000, "retained_earnings": 0, "current_profit": -80},
    liabilities={"payables": 55},
)
