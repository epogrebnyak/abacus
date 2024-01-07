from abacus import Chart

chart = Chart(
assets=["cash", "inv"],
capital=["equity"],
income=["sales"],
expenses=["cogs", "sga"],
retained_earnings_account="retained_earnings"
)

ledger = chart.ledger()
ledger.post(debit="cash", credit="equity", amount=5000, title="Shareholder investment")
ledger.post("inv",  "cash",   4000, title="Purchased merchandise")
ledger.post("cash", "sales",  4800, title="Sold merchandise")
ledger.post("cogs", "inv",    4000, title="Registered cost of sales")
ledger.post("sga",  "cash",    500, title="Paid sales representative")

from abacus import Report
report = Report(chart, ledger)
report.trial_balance.viewer.print()
report.balance_sheet.viewer.print()
report.income_statement.viewer.print()
print(report.account_balances)
