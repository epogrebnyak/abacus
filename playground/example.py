from core import Account, BalanceSheet, Chart, Ledger, Amount
from ui import NamedEntry

# Create chart of accounts with contra accounts
chart = Chart(
    assets=[Account("cash"), Account("ar"), Account("ppe", contra_accounts=["wt"])],
    capital=[Account("equity"), Account("retained_earnings")],
    liabilities=[Account("ap"), Account("ict_due"), Account("div_due")],
    income=[Account("sales", contra_accounts=["refunds", "voids"])],
    expenses=[Account("salaries"), Account("depreciation")],
).set_retained_earnings(account_name="retained_earnings")

# Create ledger from chart
ledger = Ledger.new(chart)

# Define entries and post them to ledger
entries = [
    NamedEntry("Shareholder investment")
    .amount(300)
    .debit(account_name="cash")
    .credit(account_name="equity"),
    NamedEntry("Bought office furniture").amount(200).debit("ppe").credit("cash"),
    NamedEntry("Provided services worth $200 with $100 prepayment")
    .debit("cash", 100)
    .debit("ar", 100)
    .credit("sales", 200),
    NamedEntry("Provided cashback").amount(20).debit("refunds").credit("ar"),
    NamedEntry("Received payment for services").amount(40).debit("cash").credit("ar"),
    NamedEntry("Accrued staff salaries").amount(120).debit("salaries").credit("ap"),
    NamedEntry("Accounted for office wear and tear")
    .amount(20)
    .debit("depreciation")
    .credit("wt"),
]
ledger.post_many(entries)

# TODO: accure income tax, pay 50% didividend
# What is the sequence of events at accouting period end:
# - calculate income tax

for name, (a, b) in ledger.trial_balance.tuples().items():
    print(f"{name}: {a} {b}")

# Close ledger at accounting period end
closing_entries, ledger, income_summary = ledger.close(chart)

# Show income statement data
print(income_summary.dict())
assert income_summary.dict() == {
    "income": {"sales": 180},
    "expenses": {"salaries": 120, "depreciation": 20},
}

# Show balance sheet data
# TODO: show balance sheet data with contra accounts
print(chart)
balance_sheet = BalanceSheet.new(ledger, chart)
print(balance_sheet.dict())
# - get trail balance
# - create proxy balance
# - close contra accounts
# - create BalanceSheet
# - use depreciation as example
# - maybe need name after contra accounts

# Show account balances
print(ledger.trial_balance.amounts())
assert ledger.trial_balance.amounts() == {
    "cash": 240,
    "ppe": 200,
    "equity": 300,
    "wt": 20,
    "retained_earnings": 40,
    "ap": 120,
    "ict_due": 0,
    "div_due": 0,
    "ar": 40,
}
