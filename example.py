from abacus import Chart, Entry

chart = (
    Chart()
    .asset("cash")
    .asset("goods")
    .expense("cogs")
    .capital("equity")
    .income("sales")
)

entries = [
    Entry("cash", "equity", 1000),
    Entry("goods", "cash", 500),
    Entry("cash", "sales", 750),
    Entry("cogs", "goods", 500),
]

ledger = chart.ledger().post_many(entries)
print(ledger.income_statement(chart))
print(ledger.balance_sheet(chart))
