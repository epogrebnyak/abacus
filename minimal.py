from abacus import Chart, Report

# Let's do Sample Transaction #1 from
# https://www.accountingcoach.com/accounting-basics/explanation/5
# (a great learning resource, highly recommended)

chart = Chart(assets=["cash"], capital=["common_stock"])
ledger = chart.ledger()
ledger.post(debit="cash", credit="common_stock", amount=20000)
report = Report(chart, ledger)
print(report.balance_sheet.viewer)
