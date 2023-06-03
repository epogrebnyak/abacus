from abacus import Chart

# Create chart of accounts
chart = Chart(
    assets=["cash", "receivables"],
    equity=["equity"],
    retained_earnings="re",
    liabilities=[],
    income=["services"],
    expenses=["salaries", "rent"],
)

# Account balances known from previous period end
starting_balances = {"cash": 1150, "receivables": 350, "equity": 1500}

# Create general ledger and post new entries
journal = (
    chart.journal(**starting_balances)
    .post(dr="rent", cr="cash", amount=240)
    .post(dr="services", cr="cash", amount=800)
    .post(dr="salaries", cr="cash", amount=400)
    .close()
)

# Current period profit
journal.current_profit()

# Get financial reports
journal.income_statement()
# IncomeStatement ...

journal.balance_sheet()
# BalanceSheet ...
