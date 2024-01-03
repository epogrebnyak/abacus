from fine import Chart, Report

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
ledger.post(debit="cash", credit="services", amount=3500)
ledger.post(debit="salaries", credit="cash", amount=2000)

# Print balance sheet and income statement
report = Report(chart, ledger)
print(report.trial_balance)
print(report.balance_sheet)
print(report.income_statement)

#                Balance Sheet
#  Assets    6500  Capital                6500
#    Cash    6500    Equity               5000
#                    Retained earnings    1500
#                  Liabilities               0
#  Total:    6500  Total:                 6500
#               Income Statement
#  Income                                 3500
#    Services                             3500
#  Expenses                               2000
#    Salaries                             2000
#  Current profit                         1500
