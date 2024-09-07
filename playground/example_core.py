from ui import NamedEntry

from core import T5, BalanceSheet, FastChart, IncomeStatement, Ledger

print(FastChart.default())

# Create chart of accounts with contra accounts
chart = (
    FastChart.default()
    .set_retained_earnings_account("retained_earnings")
    .set_account(T5.Asset, "cash")
    .set_account(T5.Asset, "ar")
    .set_account(T5.Asset, "ppe")
    .add_contra_account("ppe", "depreciation")
    .set_account(T5.Capital, "equity")
    .set_account(T5.Liability, "ap")
    .set_account(T5.Liability, "ict_due")
    .set_account(T5.Liability, "div_due")
    .set_account(T5.Income, "sales")
    .add_contra_account("sales", "refunds")
    .add_contra_account("sales", "voids")
    .set_account(T5.Expense, "salaries")
    .set_account(T5.Expense, "expense:depreciation")  # avoiding duplicate name
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
income_statement = IncomeStatement.new(ledger, chart)
closing_entries = ledger.close(chart)
balance_sheet = BalanceSheet.new(ledger, chart)

# Show income statement data
print(income_statement)
assert income_statement.dict() == {
    "income": {"sales": 180},
    "expenses": {"salaries": 120, "expense:depreciation": 20},
}

# Show balance sheet data
assert ledger.balances() == {
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
