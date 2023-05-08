from abacus import Chart, Entry, BalanceSheet

chart = Chart(
    assets=["cash"],
    expenses=["oh"],
    equity=["equity", "retained_earnings"],
    liabilities=["dividend_payable"],
    income=["sales"],
    contra_accounts={"sales": (["discounts"], "net_sales")},
)
entries = [
    Entry("cash", "equity", 500),  #   started a company...
    Entry("cash", "sales", 150),  #    selling thin air
    Entry("discounts", "cash", 30),  # with a discount
    Entry("oh", "cash", 50),  #        and overhead expense
]

balance_sheet = (
    chart.make_ledger()
    .process_entries(entries)
    .close("retained_earnings")
    .process_entry(dr="retained_earnings", cr="dividend_payable", amount=35)
    .balance_sheet()
)
assert balance_sheet == BalanceSheet(
    assets={"cash": 570},
    capital={"equity": 500, "retained_earnings": 35},
    liabilities={"dividend_payable": 35},
)
