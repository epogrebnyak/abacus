from composer import Chart

chart = (
    Chart()
    .asset("cash")
    .capital("equity")
    .income("services")
    .expense("marketing")
    .expense("salaries")
)
ledger = (
    chart.ledger()
    .post("cash", "equity", 5000)
    .post("marketing", "cash", 1000)
    .post("cash", "services", 3500)
    .post("salaries", "cash", 2000)
)
report = ledger.report()
report.balance_sheet().print_rich(width=45)
report.income_statement().print_rich(width=45)

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
