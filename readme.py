from abacus import Chart, Account, Report

# Define chart
chart = Chart(
    assets=["cash", "paper"],
    capital=["equity"],
    income=[Account("sales", contra_accounts=["refunds"])],
    expenses=["cogs", "salaries"],
)

# Use account balances form previous period
starting_balances = {"cash": 300, "paper": 2200, "equity": 2500}
ledger = chart.ledger(starting_balances)

# Post enties
ledger.post("cash", "sales", 2675, title="Sell paper for cash")
ledger.post("refunds", "cash", 375, title="Client refund ")
ledger.post("cogs", "paper", 2000, title="Register cost of sales")
ledger.post("salaries", "cash", 500, title="Pay salaries")

# Show reports
rename_dict = {"cogs": "Cost of goods sold", "paper": "Inventory"}
report = Report(chart, ledger, rename_dict)
report.print_all()
