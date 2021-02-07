from accounting import Chart, make_ledger, Entry, balances, print_balance

# 1. Lay out a system of accounts, or "chart of accounts", CoA.
# CoA can be standardised in some countries or businesses (eg banks).
chart = Chart(
    assets=["cash", "loans", "interest_receivable"],
    expenses=["expenses"],
    liabilities=["current_accounts", "deposits", "interest_payable"],
    capital=["equity", "retained_earnings", "provisions"],
    income=["income"],
)

# 2. Create store of data, "a ledger"
L = make_ledger(chart)

# 3. Record transactions as double entries. A double entry system
#    always affects two accounts to keep balance coherent.
transactions = [
    # Recapitalisation with owner funds
    Entry(value=100, debit="cash", credit="equity"),
    # Loans provided to clients
    Entry(80, debit="loans", credit="cash"),
    # Interest due on loans accrued
    Entry(8, debit="interest_receivable", credit="income"),
    # Сlients pay part of interest due
    Entry(5, debit="cash", credit="interest_receivable"),
]
for t in transactions:
    L.process(t)

# 4. Check resulting sums by account.
assert balances(L, chart) == {
    "cash": 25,
    "loans": 80,
    "interest_receivable": 3,
    "current_accounts": 0,
    "deposits": 0,
    "interest_payable": 0,
    "equity": 100,
    "retained_earnings": 0,
    "profit": 8,
    "provisions": 0,
}

print_balance(L, chart)