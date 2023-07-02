from abacus import Chart

chart = (
    Chart(
        assets=["cash", "ar", "goods"],
        expenses=["cogs", "sga"],
        equity=["equity"],
        liabilities=["dividend_due", "ap"],
        income=["sales"],
    )
    .set_retained_earnings("re")
    .offset("sales", ["discounts", "refunds"])
)

book = (
    chart.book()
    .post(dr="cash", cr="equity", amount=1000)
    .post(dr="goods", cr="cash", amount=250)
    .post(cr="goods", dr="cogs", amount=200)
    .post(cr="sales", dr="cash", amount=400)
    .post(cr="cash", dr="sga", amount=50)
    .close()
)

from abacus import RichViewer

income_statement = book.income_statement()
balance_sheet = book.balance_sheet()
rename_dict = {
    "re": "Retained earnings",
    "ar": "Accounts receivable",
    "ap": "Accounts payable",
    "ppe": "Fixed assets",
    "goods": "Inventory (goods for sale)",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}
rv = RichViewer(rename_dict, width=80)
rv.print(balance_sheet)
rv.print(income_statement)

from abacus import IncomeStatement, BalanceSheet

assert income_statement == IncomeStatement(
    income={"sales": 400}, expenses={"cogs": 200, "sga": 50}
)
assert balance_sheet == BalanceSheet(
    assets={"cash": 1100, "ar": 0, "goods": 50},
    capital={"equity": 1000, "re": 150},
    liabilities={"dividend_due": 0, "ap": 0},
)

end_balances = book.nonzero_balances()
assert end_balances == {"cash": 1100, "goods": 50, "equity": 1000, "re": 150}
next_book = chart.book(starting_balances=end_balances)
