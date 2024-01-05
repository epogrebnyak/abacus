from abacus import Chart, Report, echo

# Create a chart of accounts
chart = Chart(
    assets=["cash"],
    capital=["equity"],
    income=["services"],
    expenses=["marketing", "salaries"],
)

# Create a ledger using the chart
ledger = chart.ledger()

# Post entries to ledger
ledger.post(debit="cash", credit="equity", amount=5000)
ledger.post(debit="marketing", credit="cash", amount=1000)
ledger.post(debit="cash", credit="services", amount=3499)
ledger.post(debit="salaries", credit="cash", amount=2000)

# Print trial balance, balance sheet and income statement
report = Report(chart, ledger)
echo(report.trial_balance, "Trial balance")
echo(report.balance_sheet, "Balance sheet")
echo(report.income_statement, "Income statement")
print("Account balances:", report.account_balances)
