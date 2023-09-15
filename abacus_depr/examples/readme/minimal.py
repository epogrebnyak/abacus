from abacus_depr import (
    BalanceSheet,
    Chart,
    IncomeStatement,
    PlainTextViewer,
    RichViewer,
)

chart = (
    Chart(
        assets=["cash", "ar", "goods"],
        expenses=["cogs", "sga"],
        equity=["equity", "re"],
        income=["sales"],
    )
    .set_retained_earnings("re")
    .offset("sales", "discounts")
    .set_name("cogs", "Cost of goods sold")
    .set_name("sga", "Selling, general and adm.expenses")
    .set_name("goods", "Inventory (goods for sale)")
    .set_name("ar", "Accounts receivable")
)

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
)

income_statement = book.income_statement()
balance_sheet = book.balance_sheet()
tv = PlainTextViewer(rename_dict=chart.names)
tv.print(balance_sheet)
tv.print(income_statement)

rv = RichViewer(rename_dict=chart.names, width=80)
rv.print(balance_sheet)
rv.print(income_statement)

print(income_statement)
assert income_statement == IncomeStatement(
    income={"sales": 400}, expenses={"cogs": 200, "sga": 100}
)
print(balance_sheet)
assert balance_sheet == BalanceSheet(
    assets={"cash": 460, "ar": 40, "goods": 600},
    capital={"equity": 1000, "re": 100},
    liabilities={},
)

# Create next period
end_balances = book.nonzero_balances()
print(end_balances)
next_book = chart.book(starting_balances=end_balances)
