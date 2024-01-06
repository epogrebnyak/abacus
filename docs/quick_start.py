from abacus import Chart

chart = Chart(
    assets=["cash", "inventory"],
    capital=["equity"],
    income=["sales"],
    expenses=["cogs", "sga"],
    retained_earnings_account="retained_earnings",
)

ledger = chart.ledger()
ledger.post("cash", "equity", 5000, title="Shareholder investment")
ledger.post("inventory", "cash", 4000, title="Purchased merchandise")
ledger.post("cash", "sales", 4800, title="Sold merchandise")
ledger.post("cogs", "inventory", 4000, title="Registered cost of sales")
ledger.post("sga", "cash", 500, title="Paid sales representative")

from abacus import Report

report = Report(chart, ledger)
report.balance_sheet.print()
report.income_statement.print()
