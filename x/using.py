
from fine import Chart, Account, Entry, Pipeline, Reporter

chart = Chart(
    assets=["cash"],
    capital=[Account("equity", contra_accounts=["ts"])],
    income=[Account("sales", contra_accounts=["refunds", "voids"])],
    liabilities=["dd"],
    expenses=["salaries"],
)
ledger = chart.ledger()
ledger.post_many(
    [
        Entry("cash", "equity", 120),
        Entry("ts", "cash", 20),
        Entry("cash", "sales", 47),
        Entry("refunds", "cash", 5),
        Entry("voids", "cash", 2),
        Entry("salaries", "cash", 25),
    ]
)
#r = Reporter(chart, ledger)
#print(r.balance_sheet)
#print(r.income_statement)
#print(r.income_statement.current_account())
