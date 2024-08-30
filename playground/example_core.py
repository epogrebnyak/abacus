from ui import NamedEntry

from core import T5, BalanceSheet, FastChart, IncomeStatement, Ledger

# Create chart of accounts with contra accounts
chart = (
    FastChart.default()
    .set_retained_earnings("retained_earnings")
    .set_account("cash", T5.Asset)
    .set_account("ar", T5.Asset)
    .set_account("ppe", T5.Asset, ["depreciation"])
    .set_account("equity", T5.Capital)
    .set_account("ap", T5.Liability)
    .set_account("ict_due", T5.Liability)
    .set_account("div_due", T5.Liability)
    .set_account("sales", T5.Income, ["refunds", "voids"])
    .set_account("salaries", T5.Expense)
    .set_account("expense:depreciation", T5.Expense)  # avoiding duplicate name
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
assert income_statement.dict() == {
    "income": {"sales": 180},
    "expenses": {"salaries": 120, "expense:depreciation": 20},
}

# Show balance sheet data
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
