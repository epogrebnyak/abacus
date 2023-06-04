from abacus import Chart
from abacus.accounting_types import CloseExpense, CloseIncome
from abacus.ledger import yield_until

# Create chart of accounts
chart = Chart(
    assets=["cash", "goods"],
    equity=["equity"],
    retained_earnings_account="re",
    liabilities=[],
    income=["services"],
    expenses=["salaries", "rent"],
)

# Account balances known from previous period end
starting_balances = {"cash": 1150, "goods": 350, "equity": 1500}

# Create general ledger and post new entries
journal = (
    chart.journal(**starting_balances)
    .post(dr="rent", cr="cash", amount=240)
    .post(dr="cash", cr="services", amount=800)
    .post(dr="salaries", cr="cash", amount=400)
    .close()
)


from pprint import pprint

pprint(list(yield_until(journal.data, [CloseIncome, CloseExpense])))

# Current period profit
# journal.current_profit()

# Get financial reports
journal.income_statement()
# IncomeStatement ...

journal.balance_sheet()
# BalanceSheet ...
