from abacus import BaseChart, Entry, BalanceSheet, IncomeStatement

chart = (
    BaseChart(
        assets=["cash", "ar", "goods"],
        expenses=["cogs", "sga"],
        capital=["equity", "re"],
        income=["sales"],
    ).elevate()
    .set_isa("current_profit")
    .set_null("null")
    .set_re("re")
    .offset("sales", "discounts")
    .name("cogs", "Cost of goods sold")
    .name("sga", "Selling, general and adm.expenses")
    .name("goods", "Inventory (goods for sale)")
    .name("ar", "Accounts receivable")
)

ledger = (
    chart.ledger()
    .post(Entry(debit="cash", credit="equity", amount=1000))
    .post(Entry(debit="goods", credit="cash", amount=800))
    .post(Entry(debit="ar", credit="sales", amount=465))
    .post(Entry(debit="discounts", credit="ar", amount=65))
    .post(Entry(debit="cogs", credit="goods", amount=200))
    .post(Entry(debit="sga", credit="cash", amount=100))
    .post(Entry(debit="cash", credit="ar", amount=360))
)

income_statement = ledger.income_statement(chart)
income_statement.print(chart.titles)
income_statement.print_rich(chart.titles)
assert income_statement == IncomeStatement(
    income={"sales": 400}, expenses={"cogs": 200, "sga": 100}
)

ledger.close(chart)
balance_sheet = ledger.balance_sheet(chart)
balance_sheet.print(chart.titles)
balance_sheet.print_rich(chart.titles)
assert balance_sheet == BalanceSheet(
    assets={"cash": 460, "ar": 40, "goods": 600},
    capital={"equity": 1000, "re": 100},
    liabilities={},
)

# Create end of period balances
end_balances = ledger.nonzero_balances()
print(end_balances)
next_book = chart.ledger(starting_balances=end_balances)
