from abacus import Chart, IncomeStatement, BalanceSheet

# Create chart of accounts
chart = Chart(
    assets=["cash", "receivables"],
    equity=["equity"],
    retained_earnings="re",
    expenses=["salaries", "rent"],
    income=["services"],
)

# Account balances are known from previous period end
starting_balances = {"cash": 1150, "receivables": 350, "equity": 1500}

# Create general ledger and post new entries
ledger = (
    chart.ledger(**starting_balances)
    .post(dr="rent", cr="cash", amount=240)
    .post(dr="cash", cr="services",amount=800)
    .post(dr="salaries", cr="cash", amount=400)
)

# Check results
assert ledger.current_profit() == 200
assert ledger.income_statement() == IncomeStatement()
assert ledger.balance_sheet() == BalanceSheet()
assert ledger.balances() == {}

def test_current_balances():
   assert ledger.current_profit() == 200

def test_income_statement():
  assert ledger.income_statement() == IncomeStatement()

def test_balance_sheet():
  assert ledger.balance_sheet() == BalanceSheet()

def test_balances():
  assert ledger.balances() == {}
