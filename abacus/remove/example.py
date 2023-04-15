#
from accounting import Chart, Entry, balances, make_ledger

# 1. Lay out a system of accounts, or "chart of accounts", CoA.
# CoA can be standardised in some countries fully or by type of business (eg in banks).
chart = Chart(
    assets=["cash", "loans", "interest_receivable"],
    expenses=["expenses"],
    equity=["equity", "retained_earnings", "provisions"],
    liabilities=["current_accounts", "deposits", "interest_payable"],
    income=["income"],
)

# 2. Create store of data, "a ledger"
L = make_ledger(chart)

# 3. Record transactions as double entries. A double entry system
#    always affects two accounts to keep balance coherent.
transactions = [
    # Recapitalisation with owner funds
    Entry(value=30, debit="cash", credit="equity"),
    # Accept deposits
    Entry(value=60, debit="cash", credit="deposits"),
    # Loans provided to clients
    Entry(value=80, debit="loans", credit="cash"),
    # Interest due on loans accrued
    Entry(value=8, debit="interest_receivable", credit="income"),
    # Сlients pay part of interest due
    Entry(value=5, debit="cash", credit="interest_receivable"),
    # Loans claffified as bad, increase provisions
    Entry(value=15 + 3, debit="expenses", credit="provisions"),
    # Bad loan paid interest, provisions decrease
    Entry(value=10 + 2, debit="provisions", credit="income"),
    Entry(value=2, debit="cash", credit="interest_receivable"),
    # Accrue interest on deposits
    Entry(value=3, debit="expenses", credit="interest_payable"),
    Entry(value=3, debit="interest_payable", credit="current_accounts"),
]
for t in transactions:
    L.process(t)

# 4. Check resulting sums by account.
print(balances(L, chart))
assert balances(L, chart) == {
    "cash": 17,
    "loans": 80,
    "interest_receivable": 1,
    "current_accounts": 3,
    "deposits": 60,
    "interest_payable": 0,
    "equity": 30,
    "retained_earnings": 0,
    "provisions": 6,
    "profit": -1,
}

from formatting import Book

b = Book(chart, L, {})
assert b.left() == [
    "Assets",
    "  Cash.................. 17",
    "  Loans................. 80",
    "  Interest receivable...  1",
]
assert b.right() == [
    "Capital",
    "  Equity.............. 30",
    "  Retained earnings...  0",
    "  Provisions..........  6",
    "  Profit.............. -1",
    "Liabilities",
    "  Current accounts....  3",
    "  Deposits............ 60",
    "  Interest payable....  0",
]

print(b)
"""Assets                      Capital
  Cash.................. 17   Equity.............. 30
  Loans................. 80   Retained earnings...  0
  Interest receivable...  1   Provisions..........  6
                              Profit.............. -1
                            Liabilities
                              Current accounts....  3
                              Deposits............ 60
                              Interest payable....  0"""
