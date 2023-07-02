from abacus import Chart

chart = Chart(
    assets=["cash", "ar", "goods"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    liabilities=["dividend_due"],
    income=["sales"],
)
chart = chart.set_retained_earnings("re").offset("sales", ["discounts"])

book = (
    chart.book()
    .post(debit="cash", credit="equity", amount=1000)
    .post(debit="goods", credit="cash", amount=800)
    .post(debit="ar", credit="sales", amount=465)
    .post(debit="discounts", credit="ar", amount=65)
    .post(debit="cogs", credit="goods", amount=200)
    .post(debit="sga", credit="cash", amount=100)
    .post(debit="cash", credit="ar", amount=360)
    .close()
    .after_close(debit="re", credit="dividend_due", amount=50)
)

from abacus import RichViewer, PlainTextViewer

income_statement = book.income_statement()
balance_sheet = book.balance_sheet()
rename_dict = {
    "re": "Retained earnings",
    "ar": "Accounts receivable",
    "goods": "Inventory (goods for sale)",
    "cogs": "Cost of goods sold",
    "sga": "Selling, general and adm. expenses",
}

tv = PlainTextViewer(rename_dict)
tv.print(balance_sheet)
tv.print(income_statement)

rv = RichViewer(rename_dict, width=80)
rv.print(balance_sheet)
rv.print(income_statement)

from abacus import IncomeStatement, BalanceSheet

print(income_statement)
assert income_statement == IncomeStatement(
    income={"sales": 400}, expenses={"cogs": 200, "sga": 100}
)
print(balance_sheet)
assert balance_sheet == BalanceSheet(
    assets={"cash": 460, "ar": 40, "goods": 600},
    capital={"equity": 1000, "re": 50},
    liabilities={"dividend_due": 50},
)

end_balances = book.nonzero_balances()
print(end_balances)
next_book = chart.book(starting_balances=end_balances)
