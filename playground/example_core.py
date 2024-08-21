from ui import NamedEntry, create_chart

from core import BalanceSheet, Ledger

# Create chart of accounts with contra accounts
chart = (
    create_chart()
    .set_retained_earnings("retained_earnings")
    .add_asset("cash")
    .add_asset("ar")
    .add_asset("ppe", ["depreciation"])
    .add_capital("equity")
    .add_liability("ap")
    .add_liability("ict_due")
    .add_liability("div_due")
    .add_income("sales", ["refunds", "voids"])
    .add_expense("salaries")
    .add_expense("expense:depreciation")  # avoiding duplicate name
)

# Create ledger from chart
ledger = Ledger.new(chart)

# Define entries and post them to ledger
entries = [
    NamedEntry(title="Shareholder investment")
    .amount(300)
    .debit(account_name="cash")
    .credit(account_name="equity"),
    NamedEntry(title="Bought office furniture").amount(200).debit("ppe").credit("cash"),
    NamedEntry(title="Provided services worth $200 with $100 prepayment")
    .debit("cash", 100)
    .debit("ar", 100)
    .credit("sales", 200),
    NamedEntry(title="Provided cashback").amount(20).debit("refunds").credit("ar"),
    NamedEntry(title="Received payment for services")
    .amount(40)
    .debit("cash")
    .credit("ar"),
    NamedEntry(title="Accrued staff salaries")
    .amount(120)
    .debit("salaries")
    .credit("ap"),
    NamedEntry(title="Accounted for office depreciation")
    .amount(20)
    .debit("expense:depreciation")
    .credit("depreciation"),
]
ledger.post_many(entries)

# Close ledger at accounting period end
closing_entries, ledger, income_statement = ledger.close(chart)

# Show income statement data
assert income_statement.dict() == {
    "income": {"sales": 180},
    "expenses": {"salaries": 120, "expense:depreciation": 20},
}

# Show balance sheet data
balance_sheet = BalanceSheet.new(ledger, chart)

# Show account balances
assert ledger.trial_balance.amounts() == {
    "cash": 240,
    "ppe": 200,
    "equity": 300,
    "depreciation": 20,
    "retained_earnings": 40,
    "ap": 120,
    "ict_due": 0,
    "div_due": 0,
    "ar": 40,
}
