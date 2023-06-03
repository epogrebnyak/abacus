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
ledger = (
    chart.ledger(**starting_balances)
    .post(dr="rent", cr="cash", amount=240)
    .post(dr="services", cr="cash", amount=800)
    .post(dr="salaries", cr="cash", amount=400)
)

# Current period profit
ledger.current_profit()

# Get financial reports
ledger.income_statement()
# IncomeStatement ...

ledger.balance_sheet()
# BalanceSheet ...


