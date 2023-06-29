from abacus import Chart, Entry, BalanceSheet, IncomeStatement

chart = Chart(
    assets=["cash", "ar", "goods", "ppe"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    retained_earnings_account="re",
    liabilities=["dividend_due", "ap"],
    income=["sales"],
)

chart = Chart(
    assets=["cash", "ar", "goods", "ppe"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    retained_earnings_account="re",
    liabilities=["dividend_due", "ap"],
    income=["sales"],
    contra_accounts={"ppe": ["depreciation"], "sales": ["discounts", "cashback"]},
)

book = chart.book()

e1 = Entry(dr="cash", cr="equity", amount=1000)  # pay in shareholder equity
e2 = Entry(dr="goods", cr="cash", amount=250)  # acquire goods worth 250
e3 = Entry(cr="goods", dr="cogs", amount=200)  # sell goods worth 200
e4 = Entry(cr="sales", dr="cash", amount=400)  # for 400 in cash
e5 = Entry(cr="cash", dr="sga", amount=50)  # administrative expenses
book = book.post_many([e1, e2, e3, e4, e5])

book = book.close()

book = (
    chart.book()
    .post(dr="cash", cr="equity", amount=1000)
    .post(dr="goods", cr="cash", amount=250)
    .post(cr="goods", dr="cogs", amount=200)
    .post(cr="sales", dr="cash", amount=400)
    .post(cr="cash", dr="sga", amount=50)
    .close()
)

income_statement = book.income_statement()
balance_sheet = book.balance_sheet()

from abacus import IncomeStatement, BalanceSheet

assert income_statement == IncomeStatement(
    income={"sales": 400}, expenses={"cogs": 200, "sga": 50}
)
assert balance_sheet == BalanceSheet(
    assets={"cash": 1100, "ar": 0, "goods": 50, "ppe": 0},
    capital={"equity": 1000, "re": 150},
    liabilities={"dividend_due": 0, "ap": 0},
)

from abacus import RichViewer

rename_dict = {
    "re": "Retained earnings",
    "ar": "Accounts receivable",
    "ap": "Accounts payable",
    "ppe": "Fixed assets",
    "goods": "Inventory (goods for sale)",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
rv = RichViewer(rename_dict, width=60)
rv.print(balance_sheet)
rv.print(income_statement)

end_balances = book.nonzero_balances()
assert end_balances == {"cash": 1100, "goods": 50, "equity": 1000, "re": 150}
next_book = chart.book(starting_balances=end_balances)
