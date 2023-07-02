from abacus import Chart

chart = (Chart(
    assets=["cash", "ar", "goods"],
    expenses=["cogs", "sga"],
    equity=["equity"],
    liabilities=["dividend_due"],
    income=["sales"])
  .set_retained_earnings("re")
  .offset("sales", ["discounts"])
)

book = (chart.book()
  .post(dr="cash", cr="equity", amount=1000)
  .post(dr="goods", cr="cash", amount=800)
  .post(dr="ar", cr="sales", amount=965)
  .post(dr="discounts", cr="ar", amount=30)
  .post(dr="cogs", cr="goods", amount=600)
  .post(dr="sga", cr="cash", amount=185)
  .post(dr="cash", cr="ar", amount=725)
  .close()
  .after_close(dr="re", cr="dividend_due", amount=60)
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
    income={'sales': 935},
    expenses={'cogs': 600, 'sga': 185}
)
print(balance_sheet)
assert balance_sheet == BalanceSheet(
    assets={"cash": 740, "ar": 210, "goods": 200},
    capital={"equity": 1000, "re": 90},
    liabilities={"dividend_due": 60}
)

end_balances = book.nonzero_balances()
print(end_balances)
next_book = chart.book(starting_balances=end_balances)
