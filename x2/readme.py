from core import Chart, Report, Account
from show import show

# Create a chart of accounts
chart = Chart(
    assets=["cash", "prepaid_services"],
    capital=["equity"],
    income=[Account("services", contra_accounts=["cashback"])],
    liabilities=["loan"],
    expenses=["marketing", "salaries", "interest"],
)
# Create a ledger using the chart
ledger = chart.ledger()

# Post entries to ledger
ledger.post(debit="cash", credit="equity", amount=1000)
ledger.post(debit="cash", credit="loan", amount=3000)
ledger.post(debit="prepaid_services", credit="cash", amount=1800)
ledger.post(debit="salaries", credit="cash", amount=1800)
ledger.post(debit="cash", credit="services", amount=3500)
ledger.post(debit="cashback", credit="cash", amount=200)
ledger.post(debit="interest", credit="cash", amount=225)
ledger.post(debit="marketing", credit="prepaid_services", amount=1200)

# Print balance sheet and income statement
report = Report(chart, ledger)
print(show(report.trial_balance))
print(show(report.balance_sheet, {"re": "Retained earnings"}))
print(show(report.income_statement))
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
