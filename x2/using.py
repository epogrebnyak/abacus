from fine import Account, Chart, Entry, Report
from x2.print_rich import rich_print

# Trivial example: the company has cash and equity accounts
# and received $499 and $501 from two investors. What is
# the company balance sheet?

chart = Chart(assets=["cash"], capital=["equity"])
ledger = chart.ledger()
ledger.post(debit="cash", credit="equity", amount=499)
ledger.post(debit="cash", credit="equity", amount=501)
report = Report(chart, ledger)
print(report.balance_sheet)

# Chart and balances can be saved to a JSON file:

# chart.save("chart.json")
# ledger.balances.save("end_balances.json")

chart = Chart(
    assets=["cash"],
    capital=[Account("equity", contra_accounts=["ts"])],
    income=[Account("sales", contra_accounts=["refunds", "voids"])],
    liabilities=["dividend_due"],
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
        Entry("salaries", "cash", 30),
    ]
)
r = Report(chart, ledger)
print(r.balance_sheet)
print(r.income_statement)
print(r.income_statement.current_profit())
print(r.trial_balance)


rich_print(r.balance_sheet, width=60)
rich_print(r.income_statement, width=60)

from fine import T

print(T.Asset.value)
